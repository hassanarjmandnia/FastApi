from fastapi import APIRouter
from .user import user_router
from .logger import loggers

router = APIRouter()
router.include_router(user_router, prefix="/User", tags=["User"])

loggers["info"].info("API router configured successfully.")



