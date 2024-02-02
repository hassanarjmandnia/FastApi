from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from .logger import loggers
from .Database.models import User
from .cache import cache
from . import secret
import secrets

oauth_2_schemes = OAuth2PasswordBearer(tokenUrl="token")


class PasswordHashing:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.oauth_2_schemes = oauth_2_schemes

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)


class AuthManager:
    def __init__(self):
        self.secret_key = secret.SECRET_KEY
        self.refresh_secret_key = secret.REFRESH_SECRET_KEY
        self.algorithm = secret.ALGORITHM
        self.access_token_expire_minutes = secret.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_minutes = secret.REFRESH_TOKEN_EXPIRE_MINUTES

    async def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        jit = self.jit_genrator()
        to_encode.update({"exp": expire, "jit": jit})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        await cache.set(data["sub"], jit, ttl=self.refresh_token_expire_minutes * 60)
        loggers["info"].info(
            f"create a new access token for user with email {data['sub']}"
        )
        return encoded_jwt

    def create_refresh_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            minutes=self.refresh_token_expire_minutes
        )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, self.refresh_secret_key, algorithm=self.algorithm
        )
        loggers["info"].info(
            f"create a new refresh token for user with email {data['sub']}"
        )
        return encoded_jwt

    async def decode_access_token(self, token: str):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_email = payload.get("sub")
            stored_jit = await cache.get(user_email)
            if stored_jit and payload.get("jit") == stored_jit:
                return payload
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

    def decode_refresh_token(self, token: str):
        try:
            payload = jwt.decode(
                token, self.refresh_secret_key, algorithms=[self.algorithm]
            )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials(refresh token)",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def create_tokens_for_user(self, user: User):
        access_token = await self.create_access_token(data={"sub": user.email})
        refresh_token = self.create_refresh_token(data={"sub": user.email})
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    def jit_genrator(self):
        return secrets.token_urlsafe(16)
