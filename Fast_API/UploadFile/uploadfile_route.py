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
