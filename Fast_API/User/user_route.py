from .user_schemas import UserTableCreate, UserTableLogin, UserTableChangePassword
from Fast_API.Auth.auth import oauth_2_schemes, AuthManager
from Fast_API.Database.database import DatabaseManager
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
async def logout_user(logout_user: dict = Depends(UserManager().logout_user)):
    return logout_user


@user_router.post("/change_password")
async def change_password(
    change_password: dict = Depends(UserManager().change_password),
):
    return change_password


@user_router.get("/token/refresh")
async def token_refresh(
    generate_new_access_token: dict = Depends(UserManager().generate_new_access_token),
):
    return generate_new_access_token


@user_router.get("/token/re654fresh")
async def token_refresh(
    token: str = Depends(oauth_2_schemes),
    user_manager: UserManager = Depends(UserManager),
):
    return await user_manager.generate_new_access_token(token)


@user_router.get("/token/check")
async def token_check(token: str = Depends(oauth_2_schemes)):
    payload = await AuthManager().decode_access_token(token)
    return {"message": "Secure Data", "token_payload": payload}
