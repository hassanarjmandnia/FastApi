from .user_schemas import UserTableCreate, UserTableLogin, UserTableChangePassword
from Fast_API.Auth.auth import AuthManager, PasswordHashing, oauth_2_schemes
from Fast_API.utils.validators import validate_unique_email
from Fast_API.Database.user_db import UserDatabaseAction
from Fast_API.Database.role_db import RoleDatabaseAction
from fastapi import Depends, HTTPException, status
from Fast_API.Database.models import User, Role
from Fast_API.utils.logger import loggers
from Fast_API.utils.cache import cache
from sqlalchemy.orm import Session
from datetime import datetime

PASSWORD_CHANGE_THRESHOLD = 60


class UserAction:
    def __init__(
        self, auth_manager, password_manager, user_database_action, role_database_action
    ):
        self.auth_manager = auth_manager
        self.password_manager = password_manager
        self.user_database_action = user_database_action
        self.role_database_action = role_database_action

    def add_new_user(self, user: UserTableCreate, db_session):
        validate_unique_email(user.email, db_session)
        new_user = User(
            **user.model_dump(exclude={"password", "password_confirmation"}),
            password=self.password_manager.get_password_hash(user.password),
        )
        self.set_default_role(new_user, db_session)
        self.user_database_action.add_user(new_user, db_session)
        loggers["info"].info(f"New user {new_user.email} add to databse")
        return new_user

    def set_default_role(self, user: User, db_session):
        if not user.role:
            default_role = self.role_database_action.get_role_by_name(
                "user", db_session
            )
            if not default_role:
                default_role = Role(name="user")
                self.role_database_action.add_role(default_role, db_session)
            user.role = default_role

    def authenticate_user(self, email: str, password: str, db_session):
        user = self.user_database_action.get_user_by_email(email, db_session)
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

    def check_if_user_is_active(self, user):
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
        payload = await self.auth_manager.decode_access_token(token)
        user_email = payload.get("sub")
        await cache.set(user_email, None)
        loggers["info"].info(f"User {user_email} Logout successfuly")
        return {"message": "Logout successful"}

    async def update_password(self, user: UserTableChangePassword, db_session):
        authenticated_user = self.authenticate_user(
            user.email, user.password, db_session
        )
        authenticated_user.password = self.password_manager.get_password_hash(
            user.new_password
        )
        authenticated_user.last_password_change = datetime.now()
        self.user_database_action.commit_changes(db_session)
        self.user_database_action.refresh_item(authenticated_user, db_session)

        stored_jit = await cache.get(user.email)
        if stored_jit:
            await cache.set(user.email, None)
        loggers["info"].info(f"User {authenticated_user.email} changed their password")
        return {"message": "Password successfully changed"}

    def get_user_info(self, email, db_session):
        user = self.user_database_action.get_user_by_email(email, db_session)
        return user


class UserManager:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.auth_manager = AuthManager()
            cls._instance.password_manager = PasswordHashing()
            cls._instance.user_database_action = UserDatabaseAction()
            cls._instance.role_database_action = RoleDatabaseAction()
            cls._instance.worker = UserAction(
                cls._instance.auth_manager,
                cls._instance.password_manager,
                cls._instance.user_database_action,
                cls._instance.role_database_action,
            )

        return cls._instance

    async def register_user(self, user: UserTableCreate, db_session: Session):
        user = self.worker.add_new_user(user, db_session)
        return await self.auth_manager.create_tokens_for_user(user)

    async def login_user(self, user: UserTableLogin, db_session: Session):
        user = self.worker.authenticate_user(user.email, user.password, db_session)
        if self.worker.check_if_user_is_active(user):
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

    async def change_password(self, user: UserTableChangePassword, db_session):
        return await self.worker.update_password(user, db_session)

    async def find_user_info(self, token: str, db_session):
        payload = await self.auth_manager.decode_access_token(token)
        user = self.worker.get_user_info(payload.get("sub"), db_session)
        return user
