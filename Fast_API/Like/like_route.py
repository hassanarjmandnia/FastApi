from Fast_API.Database.database import DatabaseManager
from Fast_API.User.user_modules import UserManager
from Fast_API.Database.models import User
from fastapi import APIRouter, Depends
from .like_modules import LikeManager
from sqlalchemy.orm import Session
from typing import Union

like_router = APIRouter()


@like_router.post("/like_note/{note_id}")
async def like_unlike_note(
    note_id: int,
    current_user: User = Depends(UserManager().get_current_user),
    db_session: Session = Depends(DatabaseManager().get_session),
    like_manager: LikeManager = Depends(LikeManager),
):
    return await like_manager.like_unlike_note(note_id, current_user, db_session)


@like_router.get("/likers/{note_id}")
async def likers_of_note(
    note_id: int,
    current_user: User = Depends(UserManager().get_current_user),
    db_session: Session = Depends(DatabaseManager().get_session),
    like_manager: LikeManager = Depends(LikeManager),
):
    return await like_manager.likers_of_note(note_id, db_session)


@like_router.get("/likes")
async def likes_of_user(
    current_user: User = Depends(UserManager().get_current_user),
    db_session: Session = Depends(DatabaseManager().get_session),
    like_manager: LikeManager = Depends(LikeManager),
):
    return await like_manager.likes_of_user(current_user, db_session)
