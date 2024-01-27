from pydantic import BaseModel, Field, validator, EmailStr
from fastapi import HTTPException, status, Depends
from typing import Optional


class UserTableCreate(BaseModel):
    first_name: str = Field(..., min_length=3)
    last_name: str = Field(..., min_length=6)
    email: EmailStr = Field(..., min_length=7)
    password: str = Field(..., min_length=7)
    password_confirmation: str = Field(..., min_length=7)

    @validator("password_confirmation")
    def passwords_match(cls, password_confirmation, values):
        if "password" in values and password_confirmation != values["password"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match.",
            )


class UserTableLogin(BaseModel):
    email: EmailStr = Field(..., min_length=7)
    password: str = Field(..., min_length=7)


class UserTableChangePassword(BaseModel):
    email: EmailStr = Field(..., min_length=7)
    password: str = Field(..., min_length=7)
    new_password: str = Field(..., min_length=7)
    new_password_confirmation: str = Field(..., min_length=7)

    @validator("new_password_confirmation")
    def passwords_match(cls, new_password_confirmation, values):
        if (
            "new_password" in values
            and new_password_confirmation != values["new_password"]
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match.",
            )
        return new_password_confirmation


class UserTableResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str


class UserTableUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=3)
    last_name: Optional[str] = Field(None, min_length=6)
    email: Optional[str] = Field(None, min_length=7)

    def at_least_one_field_is_provided(self):
        if self.first_name is None and self.last_name is None and self.email is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Are you sure you want to update anything? At least one field (first name or last name or email) should be provided.",
            )
