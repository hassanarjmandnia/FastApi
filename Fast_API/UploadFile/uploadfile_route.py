from .uploadfile_modules import UploadFileManager
from fastapi import APIRouter, Depends
from fastapi import File, UploadFile
from typing import List

from Fast_API.Database.database import get_mongo_database
from .uploadfile_schemas import User
from fastapi import HTTPException
from bson import ObjectId
from bson.errors import InvalidId

uploadfile_router = APIRouter()
db = get_mongo_database("mongo_test")


@uploadfile_router.post("/create")
async def write_to_mongo(user: User):
    user_dict = user.model_dump()
    result = db.users.insert_one(user_dict)
    return {"message": "User created successfully", "id": str(result.inserted_id)}


@uploadfile_router.get("/read/{user_id}")
async def read_user(user_id: str):
    try:
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            # Convert ObjectId to string
            user["_id"] = str(user["_id"])
            return user
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ObjectId")


@uploadfile_router.put("/update/{user_id}")
async def update_user(user_id: str, user: User):
    try:
        user_dict = user.model_dump()
        result = db.users.update_one({"_id": ObjectId(user_id)}, {"$set": user_dict})
        if result.modified_count == 1:
            return {"message": "User updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ObjectId")


@uploadfile_router.delete("/delete/{user_id}")
async def delete_user(user_id: str):
    try:
        result = db.users.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 1:
            return {"message": "User deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ObjectId")


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
