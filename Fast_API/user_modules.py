from .schemas import UserTableCreate, UserTableLogin, UserTableChangePassword
from .database import DatabaseManager, GeneralDatabaseAction
from fastapi import HTTPException, Depends, status
from .auth import AuthManager, PasswordHashing
from .validators import validate_unique_email
from sqlalchemy.orm import Session
from .models import User, Role
from jose import JWTError, jwt
from datetime import datetime
from .logger import loggers
from .cache import cache
from . import secret

PASSWORD_CHANGE_THRESHOLD = 90


class UserAction(GeneralDatabaseAction):
    def __init__(self, db: Session, auth_manager, password_manager):
        super().__init__(db)
        self.auth_manager = auth_manager
        self.password_manager = password_manager

    def add_user(self, user: UserTableCreate):
        new_user = User(
            **user.model_dump(exclude={"password", "password_confirmation"}),
            password=self.password_manager.get_password_hash(user.password),
        )
        self.set_default_role(new_user)
        self.add_item(new_user)
        self.commit_changes()
        self.refresh_item(new_user)
        loggers["info"].info(f"New user {new_user.email} add to databse")
        return new_user

    def set_default_role(self, user: User):
        if not user.role:
            default_role = self.db.query(Role).filter_by(name="user").first()
            if not default_role:
                default_role = Role(name="user")
                self.add_item(default_role)
                self.commit_changes()
            user.role = default_role

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
        print(days_since_last_change)
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


class UserManager:
    def __init__(self, db: Session = Depends(DatabaseManager().get_session)):
        self.db = db
        self.auth_manager = AuthManager()
        self.password_manager = PasswordHashing()
        self.worker = UserAction(self.db, self.auth_manager, self.password_manager)

    async def register_user(self, user: UserTableCreate):
        validate_unique_email(user.email, self.db)
        user = self.worker.add_user(user)
        return await self.auth_manager.create_tokens_for_user(user)

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
