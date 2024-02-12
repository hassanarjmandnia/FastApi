from fastapi import APIRouter

uploadfile_router = APIRouter()


@uploadfile_router.post("/uploadfile")
async def upload_file():
    return "upload file"
