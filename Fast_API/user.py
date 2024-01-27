from .schemas import UserTableCreate, UserTableLogin, UserTableChangePassword
from .auth import oauth_2_schemes, AuthManager
from fastapi import APIRouter, Depends
from .user_modules import UserManager
from .logger import loggers


user_router = APIRouter()


@user_router.post("/register")
async def register_user(
    user: UserTableCreate,
    user_manager: UserManager = Depends(UserManager),
):
    return await user_manager.register_user(user)


@user_router.post("/login")
async def login_user(
    user: UserTableLogin,
    user_manager: UserManager = Depends(UserManager),
):
    return await user_manager.login_user(user)


@user_router.get("/logout")
async def logout_user(
    token: str = Depends(oauth_2_schemes),
    user_manager: UserManager = Depends(UserManager),
):
    return await user_manager.logout_user(token)


@user_router.get("/token/check")
async def token_check(token: str = Depends(oauth_2_schemes)):
    payload = await AuthManager().decode_access_token(token)
    return {"message": "Secure Data", "token_payload": payload}


@user_router.get("/token/refresh")
async def token_refresh(
    token: str = Depends(oauth_2_schemes),
    user_manager: UserManager = Depends(UserManager),
):
    return await user_manager.generate_new_access_token(token)


@user_router.post("/change_password")
async def change_password(
    user: UserTableChangePassword,
    user_manager: UserManager = Depends(UserManager),
):
    return await user_manager.change_password(user)
