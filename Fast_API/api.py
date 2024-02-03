from fastapi import APIRouter
from Fast_API.User.user_route import user_router
from .note import note_router
from .logger import loggers

router = APIRouter()
router.include_router(user_router, prefix="/User", tags=["User"])
router.include_router(note_router, prefix="/Note", tags=["Note"])

loggers["info"].info("API router configured successfully.")
