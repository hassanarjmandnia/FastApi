from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from .Database.models import User


def validate_unique_email(email: str, user_database_action):
    # user = db.query(User).filter(User.email == email).first()
    user = user_database_action.get_user_by_email(email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )
