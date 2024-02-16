from fastapi import File, HTTPException, Response, UploadFile, status
from Fast_API.Database.database import get_mongo_database
from bson.errors import InvalidId
from typing import List, Dict
import concurrent.futures
from gridfs import GridFS
from bson import ObjectId
import zipfile
import shutil
import json
import re
import os


ALLOWED_EXTENSIONS = {"txt", "zip", "json"}


class UploadFileAction:
    def __init__(self):
        self.db = get_mongo_database("processed_files")
        self.fs = GridFS(self.db)

    def allowed_file(self, filename: str) -> bool:
        return (
            "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
        )

    async def extract_zip_file(self, zip_file: UploadFile, output_folder: str):
        extracted_txt_files = []
        with zipfile.ZipFile(zip_file.file, "r") as zip_ref:
            for member in zip_ref.infolist():
                if member.filename.endswith(".json"):
                    zip_ref.extract(member, output_folder)
                    extracted_txt_files.append(
                        os.path.join(output_folder, member.filename)
                    )
        return extracted_txt_files

    async def get_path_of_files(self, files: list[UploadFile] = File(...)):
        path = []
        for uploaded_file in files:
            if not self.allowed_file(uploaded_file.filename):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only .txt and .zip files are allowed",
                )
            if uploaded_file.filename.endswith(".txt"):
                output_folder = os.path.expanduser("~/Desktop/Files/TxtFiles")
                os.makedirs(output_folder, exist_ok=True)
                file_path = os.path.join(output_folder, uploaded_file.filename)
                with open(file_path, "wb") as f:
                    shutil.copyfileobj(uploaded_file.file, f)
                path.append(file_path)
            elif uploaded_file.filename.endswith(".zip"):
                output_folder = os.path.expanduser(
                    f"~/Desktop/Files/extractedzipfiles/{uploaded_file.filename}"
                )
                os.makedirs(output_folder, exist_ok=True)
                extracted_txt_files = await self.extract_zip_file(
                    uploaded_file, output_folder
                )
                path.extend(extracted_txt_files)
        return path

    def worker_1(self, data, file_path):
        for item in data:
            tweet_info = item.get("_", {})
            tweet_type = tweet_info.get("type", "")
            if tweet_type == "tweet":
                item = self.worker_2(item)
        # self.worker_3(data, file_path)
        self.worker_4(data, file_path)

    def worker_2(self, item):
        text_content = item.get("text", "")
        hashtags = re.findall(r"#(\w+)", text_content)
        item["_"]["hashtags"] = hashtags
        return item

    def worker_3(self, data, file_path):
        file_name = os.path.basename(file_path)
        original_dir = os.path.dirname(file_path)
        new_folder_path = os.path.join(original_dir, "new")
        os.makedirs(new_folder_path, exist_ok=True)
        new_file_path = os.path.join(
            new_folder_path, "new_" + os.path.basename(file_name)
        )
        with open(new_file_path, "w", encoding="utf-8") as new_file:
            json.dump(data, new_file, ensure_ascii=False, indent=4)

    def worker_4(self, data, file_path):
        file_name = os.path.basename(file_path)
        encoded_data = json.dumps(data).encode("utf-8")
        file_id = self.fs.put(encoded_data, filename=file_name)
        return file_id

    def process_single_file(self, file_path):
        file_name = os.path.basename(file_path)
        with open(file_path, "r", encoding="utf-8") as file:
            decoder = json.JSONDecoder()
            data = decoder.decode(file.read())
        self.worker_1(data, file_name, file_path)
        return "ok"

    async def concurrent_process_file(self, file_paths):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.process_single_file, file_path)
                for file_path in file_paths
            ]

            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        return results

    async def process_file(self, file_paths):
        for file_path in file_paths:
            with open(file_path, "r", encoding="utf-8") as file:
                decoder = json.JSONDecoder()
                data = decoder.decode(file.read())
            self.worker_1(data, file_path)
        return "ok"

    def get_list_of_files(self):
        files = []
        for file in self.fs.find():
            files.append({"id": str(file._id), "name": file.filename})
        return files

    def get_file_by_id(self, file_id: str) -> List[Dict]:
        try:
            file_object = self.fs.get(ObjectId(file_id))
            if file_object:
                file_content = json.loads(file_object.read().decode("utf-8"))
                reduced_content = []
                for item in file_content:
                    reduced_item = {
                        "_": item["_"],
                        "update_time": item.get("update_time", ""),
                        "id": item.get("id", ""),
                        "created_at": item.get("created_at", ""),
                        "text": item.get("text", ""),
                        "full_text": item.get("full_text", ""),
                    }
                    reduced_content.append(reduced_item)
                return reduced_content
            else:
                raise HTTPException(status_code=404, detail="File not found")
        except InvalidId:
            raise HTTPException(status_code=400, detail="Invalid ObjectId")

    def update_items_of_file(self, file_id: str, updated_data: dict):
        try:
            try:
                file_object = self.fs.get(ObjectId(file_id))
                file_content = json.loads(file_object.read().decode("utf-8"))
                for item in file_content:
                    if item.get("id") == updated_data.get("id"):
                        for key, value in updated_data.items():
                            if key != "id":
                                item[key] = value
                        encoded_data = json.dumps(file_content).encode("utf-8")
                        self.fs.delete(ObjectId(file_id))
                        self.fs.put(
                            encoded_data,
                            filename=file_object.filename,
                            content_type=file_object.content_type,
                            _id=file_object._id,
                        )
                        return {"message": "File updated successfully"}
                    else:
                        return {"message": "This file don't have a item with this id"}
            except Exception as e:
                raise HTTPException(status_code=404, detail="File not found")
        except InvalidId:
            raise HTTPException(status_code=400, detail="Invalid ObjectId")


class UploadFileManager:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.worker = UploadFileAction()
        return cls._instance

    async def process_uploaded_files(self, files: list[UploadFile] = File(...)):
        file_paths = await self.worker.get_path_of_files(files)
        return await self.worker.process_file(file_paths)

    async def concurrent_process_uploaded_files(
        self, files: list[UploadFile] = File(...)
    ):
        file_paths = await self.worker.get_path_of_files(files)
        return await self.worker.concurrent_process_file(file_paths)

    def get_list_of_files(self):
        return self.worker.get_list_of_files()

    def get_file_by_id(self, file_id: str):
        return self.worker.get_file_by_id(file_id)

    def update_items_of_file(self, file_id: str, updated_data: dict):
        return self.worker.update_items_of_file(file_id, updated_data)
