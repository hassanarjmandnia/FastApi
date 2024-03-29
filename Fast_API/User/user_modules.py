from .user_schemas import UserTableCreate, UserTableLogin, UserTableChangePassword
from Fast_API.Auth.auth import AuthManager, PasswordHashing, oauth_2_schemes
from Fast_API.utils.validators import validate_unique_email
from fastapi import Depends, HTTPException, Request, status
from Fast_API.Database.user_db import UserDatabaseAction
from Fast_API.Database.role_db import RoleDatabaseAction
from Fast_API.Database.database import DatabaseManager
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
        new_user = self.user_database_action.add_user(new_user, db_session)
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

    async def invalid_token(self, token):
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

    async def extract_token_from_request(self, request: Request):
        token = request.headers.get("Authorization")
        if token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_type, token_data = token.split()
        if token_type.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return token_data

    async def create_new_access_token(self, refresh_token):
        payload = self.auth_manager.decode_refresh_token(refresh_token)
        user_email = payload.get("sub")
        stored_jit = await cache.get(user_email)
        if stored_jit is not None:
            new_access_token = await self.auth_manager.create_access_token(
                data={"sub": user_email}
            )
            return {"access token": new_access_token}
        return {"Login Required"}

    async def get_user_from_token(self, access_token, db_session):
        payload = await self.auth_manager.decode_access_token(access_token)
        user_email = payload.get("sub")
        user = self.user_database_action.get_user_by_email(user_email, db_session)
        return user

    def check_role_of_user(self, role_id, role, db_session):
        if self.role_database_action.find_role_name(role_id, db_session) == role:
            return True
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a SuperAdmin",
            )


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

    async def register_user(
        self,
        user: UserTableCreate,
        db_session: Session = Depends(DatabaseManager().get_session),
    ):
        user = self.worker.add_new_user(user, db_session)
        return await self.auth_manager.create_tokens_for_user(user)

    async def login_user(
        self,
        user: UserTableLogin,
        db_session: Session = Depends(DatabaseManager().get_session),
    ):
        user = self.worker.authenticate_user(user.email, user.password, db_session)
        if self.worker.check_if_user_is_active(user):
            if self.worker.last_password_change_check(user):
                return await self.auth_manager.create_tokens_for_user(user)

    async def logout_user(self, token: str):
        return await self.worker.invalid_token(token)

    async def generate_new_access_token(self, refresh_token):
        return await self.worker.create_new_access_token(refresh_token)

    async def change_password(
        self,
        user: UserTableChangePassword,
        db_session: Session = Depends(DatabaseManager().get_session),
    ):
        return await self.worker.update_password(user, db_session)

    async def get_token_from_request(self, request: Request):
        return await self.worker.extract_token_from_request(request)

    async def get_current_user(
        self,
        request: Request,
        db_session: Session = Depends(DatabaseManager().get_session),
    ):
        access_token = await self.get_token_from_request(request)
        return await self.worker.get_user_from_token(access_token, db_session)

    async def authenticate_and_verify_super_admin(
        self,
        request: Request,
        db_session: Session = Depends(DatabaseManager().get_session),
    ):
        user = await self.get_current_user(request, db_session)
        if self.worker.check_role_of_user(user.role_id, "superadmin", db_session):
            return user
