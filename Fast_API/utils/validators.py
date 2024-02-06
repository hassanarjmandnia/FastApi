from Fast_API.Database.user_db import UserDatabaseAction
from fastapi import HTTPException, status


def validate_unique_email(email: str, db_session):
    user_database_action = UserDatabaseAction()
    user = user_database_action.get_user_by_email(email, db_session)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )
