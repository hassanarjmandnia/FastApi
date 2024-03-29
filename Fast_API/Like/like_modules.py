from Fast_API.Database.like_db import LikeDatabaseAction
from Fast_API.Database.models import User, Like
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session


class LikeAction:
    def __init__(self, like_database_action):
        self.like_database_action = like_database_action

    async def like_unlike_note(self, note_id: int, user: User, db_session: Session):
        existing_like = self.like_database_action.get_existing_like(
            user.id, note_id, db_session
        )
        if existing_like:
            self.like_database_action.delete_like(existing_like, db_session)
            message = "you unlike this note"
            status_code = 200
            return JSONResponse(content={"message": message}, status_code=status_code)
        else:
            new_like = Like(user_id=user.id, note_id=note_id)
            self.like_database_action.add_like(new_like, db_session)
            message = "you like this note"
            status_code = 200
            return JSONResponse(content={"message": message}, status_code=status_code)

    async def likers_of_note(self, note_id: int, db_session: Session):
        likes = self.like_database_action.get_all_likes_of_a_note(note_id, db_session)
        users_who_liked_note = [(like.user) for like in likes]
        return users_who_liked_note

    async def likes_of_user(self, user: User, db_session: Session):
        likes = self.like_database_action.get_all_likes_from_a_user(user.id, db_session)
        notes_liked_by_user = [like.note for like in likes]
        return notes_liked_by_user


class LikeManager:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.like_database_action = LikeDatabaseAction()
            cls._instance.worker = LikeAction(cls._instance.like_database_action)
        return cls._instance

    async def like_unlike_note(self, note_id: int, user: User, db_session: Session):
        return await self.worker.like_unlike_note(note_id, user, db_session)

    async def likers_of_note(self, note_id: int, db_session: Session):
        return await self.worker.likers_of_note(note_id, db_session)

    async def likes_of_user(self, user: User, db_session: Session):
        return await self.worker.likes_of_user(user, db_session)
