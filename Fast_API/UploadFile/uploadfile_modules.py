from fastapi import File, HTTPException, UploadFile, status
from typing import List
import zipfile
import shutil
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

    async def process_file(self, file_paths):
        file_names = [os.path.basename(path) for path in file_paths]
        return file_names


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
