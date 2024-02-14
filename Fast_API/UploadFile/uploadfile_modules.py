from fastapi import File, HTTPException, UploadFile, status
from typing import List
import zipfile
import shutil
import json
import re
import os


ALLOWED_EXTENSIONS = {"txt", "zip", "json"}


class UploadFileAction:
    def __init__(self):
        pass

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

    def worker_1(self, data, file_name, file_path):
        for item in data:
            tweet_info = item.get("_", {})
            tweet_type = tweet_info.get("type", "")
            if tweet_type == "tweet":
                item = self.worker_2(item)
        self.worker_3(data, file_name, file_path)

    def worker_2(self, item):
        text_content = item.get("text", "")
        hashtags = re.findall(r"#(\w+)", text_content)
        item["_"]["hashtags"] = hashtags
        return item

    def worker_3(self, data, file_name, file_path):
        original_dir = os.path.dirname(file_path)
        new_folder_path = os.path.join(original_dir, "new")
        os.makedirs(new_folder_path, exist_ok=True)
        new_file_path = os.path.join(
            new_folder_path, "new_" + os.path.basename(file_name)
        )
        with open(new_file_path, "w", encoding="utf-8") as new_file:
            json.dump(data, new_file, ensure_ascii=False, indent=4)

    async def process_file(self, file_paths):
        for file_path in file_paths:
            file_name = os.path.basename(file_path)
            with open(file_path, "r", encoding="utf-8") as file:
                decoder = json.JSONDecoder()
                data = decoder.decode(file.read())
            self.worker_1(data, file_name, file_path)
        return "ok"


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
