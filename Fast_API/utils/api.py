from Fast_API.Superadmin.superadmin_route import superadmin_router
from Fast_API.User.user_route import user_router
from Fast_API.Note.note_route import note_router
from Fast_API.Like.like_route import like_router

from fastapi import APIRouter
from .logger import loggers

router = APIRouter()
router.include_router(user_router, prefix="/User", tags=["User"])
router.include_router(note_router, prefix="/Note", tags=["Note"])
router.include_router(like_router, prefix="/Like", tags=["Like"])
router.include_router(superadmin_router, prefix="/Superadmin", tags=["Superadmin"])

loggers["info"].info("API router configured successfully.")
