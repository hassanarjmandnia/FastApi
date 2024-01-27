from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from .models import User


def validate_unique_email(email: str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )
