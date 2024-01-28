from .schemas import UserTableCreate, UserTableLogin, UserTableChangePassword
from .auth import oauth_2_schemes, AuthManager
from fastapi import APIRouter, Depends
from .user_modules import UserManager
from .logger import loggers


note_router = APIRouter()


@note_router.get("/test")
async def test():
    return await {"Hello world": "from note.py"}
