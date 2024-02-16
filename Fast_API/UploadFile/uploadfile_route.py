from .uploadfile_modules import UploadFileManager
from fastapi import APIRouter, Depends
from fastapi import File, UploadFile
from typing import List

uploadfile_router = APIRouter()


@uploadfile_router.post("/uploadfile")
async def upload_files(
    files: List[UploadFile] = File(...),
    upload_manager: UploadFileManager = Depends(UploadFileManager),
):
    return await upload_manager.process_uploaded_files(files)


@uploadfile_router.post("/concurrent_uploadfile")
async def concurrent_upload_files(
    files: List[UploadFile] = File(...),
    upload_manager: UploadFileManager = Depends(UploadFileManager),
):
    return await upload_manager.concurrent_process_uploaded_files(files)


@uploadfile_router.get("/files")
async def get_list_of_files(
    upload_manager: UploadFileManager = Depends(UploadFileManager),
):
    return upload_manager.get_list_of_files()


@uploadfile_router.get("/files/{file_id}")
async def get_file_by_id(
    file_id: str, upload_manager: UploadFileManager = Depends(UploadFileManager)
):
    return upload_manager.get_file_by_id(file_id)


@uploadfile_router.put("/files/{file_id}")
async def update_file_data(
    file_id: str,
    updated_data: dict,
    upload_manager: UploadFileManager = Depends(UploadFileManager),
):
    return upload_manager.update_items_of_file(file_id, updated_data)
