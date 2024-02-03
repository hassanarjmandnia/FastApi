from pydantic import BaseModel, Field, validator, EmailStr
from fastapi import HTTPException, status
from typing import Optional


class NoteTableAdd(BaseModel):
    data: str = Field(..., min_length=7)
