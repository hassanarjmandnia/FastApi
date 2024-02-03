from .user_schemas import UserTableCreate, UserTableLogin, UserTableChangePassword
from Fast_API.auth import AuthManager, PasswordHashing, oauth_2_schemes
from Fast_API.Database.database import GeneralDatabaseAction
from fastapi import HTTPException, Depends, status
from ..validators import validate_unique_email
from sqlalchemy.orm import Session
from ..Database.models import User, Role
from jose import JWTError, jwt
from datetime import datetime
from ..logger import loggers
from ..cache import cache
from .. import secret
from Fast_API.Database.user_db import UserDatabaseAction
from Fast_API.Database.role_db import RoleDatabaseAction
from Fast_API.Database.database import DatabaseManager

PASSWORD_CHANGE_THRESHOLD = 60


class UserAction:
    def __init__(self, auth_manager, password_manager, db_session):
        self.auth_manager = auth_manager
        self.password_manager = password_manager
        self.user_database_action = UserDatabaseAction(db_session)
        self.role_database_action = RoleDatabaseAction(db_session)

    def add_new_user(self, user: UserTableCreate):
        validate_unique_email(user.email, self.user_database_action)
        new_user = User(
            **user.model_dump(exclude={"password", "password_confirmation"}),
            password=self.password_manager.get_password_hash(user.password),
        )
        self.set_default_role(new_user)
        self.user_database_action.add_user(new_user)
        loggers["info"].info(f"New user {new_user.email} add to databse")
        return new_user

    def set_default_role(self, user: User):
        if not user.role:
            default_role = self.role_database_action.get_role_by_name("user")
            if not default_role:
                default_role = Role(name="user")
                self.role_database_action.add_role(default_role)
            user.role = default_role


class UserManager:
    def __init__(
        self,
        db_session: Session = Depends(DatabaseManager().get_session),
    ):
        self.db_session = db_session
        self.auth_manager = AuthManager()
        self.password_manager = PasswordHashing()
        self.worker = UserAction(
            self.auth_manager, self.password_manager, self.db_session
        )

    async def register_user(self, user: UserTableCreate):
        user = self.worker.add_new_user(user)
        return await self.auth_manager.create_tokens_for_user(user)


"""


def authenticate_user(
    self,
    email: str,
    password: str,
):
    user = self.db.query(User).filter(User.email == email).first()
    if not user or not self.password_manager.verify_password(
        password, user.password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials (user-pass)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    loggers["info"].info(f"User {user.email} Logged-in")
    return user

def user_is_active_check(self, user):
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not active, Activation Required!",
        )
    return True

def last_password_change_check(self, user):
    days_since_last_change = (datetime.now() - user.last_password_change).days
    if days_since_last_change > PASSWORD_CHANGE_THRESHOLD:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please change your password!",
        )
    return True

async def invalid_token(self, token: str):
    try:
        payload = jwt.decode(
            token, secret.SECRET_KEY, algorithms=[secret.ALGORITHM]
        )
        user_email = payload.get("sub")
        stored_jit = await cache.get(user_email)
        if stored_jit:
            await cache.set(user_email, None)
            loggers["info"].info(f"User {user_email} Logout successfuly")
            return {"message": "Logout successful"}
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials (access token)",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def update_password(self, user: UserTableChangePassword):
    authenticated_user = self.authenticate_user(user.email, user.password)
    authenticated_user.password = self.password_manager.get_password_hash(
        user.new_password
    )
    authenticated_user.last_password_change = datetime.now()
    self.commit_changes()
    self.refresh_item(authenticated_user)
    stored_jit = await cache.get(user.email)
    if stored_jit:
        await cache.set(user.email, None)
    loggers["info"].info(f"User {authenticated_user.email} changed their password")
    return {"message": "Password successfully changed"}

def get_user_info(self, email):
    print(email)
    user = self.db.query(User).filter(User.email == email).first()
    return user
"""

"""
async def login_user(self, user: UserTableLogin):
    user = self.worker.authenticate_user(user.email, user.password)
    if self.worker.user_is_active_check(user):
        if self.worker.last_password_change_check(user):
            return await self.auth_manager.create_tokens_for_user(user)


async def logout_user(self, token: str):
    return await self.worker.invalid_token(token)


async def generate_new_access_token(self, refresh_token: str):
    payload = self.auth_manager.decode_refresh_token(refresh_token)
    user_email = payload.get("sub")
    stored_jit = await cache.get(user_email)
    if stored_jit is not None:
        new_access_token = await self.auth_manager.create_access_token(
            data={"sub": user_email}
        )
        return {"access token": new_access_token}
    return {"Login Required"}


async def change_password(self, user: UserTableChangePassword):
    return await self.worker.update_password(user)


async def find_user_info(
    self,
    token: str = Depends(oauth_2_schemes),
):
    print("here")
    payload = await self.auth_manager.decode_access_token(token)
    user = self.worker.get_user_info(payload.get("sub"))
    return user
"""
