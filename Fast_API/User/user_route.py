from Fast_API.Auth.auth import oauth_2_schemes, AuthManager
from Fast_API.Database.database import DatabaseManager
from Fast_API.Database.models import User
from fastapi import APIRouter, Depends
from .user_modules import UserManager
from sqlalchemy.orm import Session


user_router = APIRouter()


@user_router.post("/register")
async def register_user(register_user: dict = Depends(UserManager().register_user)):
    return register_user


@user_router.post("/login")
async def login_user(login_user: dict = Depends(UserManager().login_user)):
    return login_user


@user_router.get("/logout")
async def logout_user(
    token: str = Depends(UserManager().get_token_from_request),
    user_manager: UserManager = Depends(UserManager),
):
    return await user_manager.logout_user(token)


@user_router.post("/change_password")
async def change_password(
    change_password: dict = Depends(UserManager().change_password),
):
    return change_password


@user_router.get("/token/refresh")
async def token_refresh(
    refresh_token: str = Depends(UserManager().get_token_from_request),
    user_manager: UserManager = Depends(UserManager),
):
    return await user_manager.generate_new_access_token(refresh_token)


@user_router.get("/token/check")
async def token_check(token: str = Depends(oauth_2_schemes)):
    payload = await AuthManager().decode_access_token(token)
    return {"message": "Secure Data", "token_payload": payload}
