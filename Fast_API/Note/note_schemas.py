from pydantic import BaseModel, Field
from datetime import datetime


class NoteTableAdd(BaseModel):
    data: str = Field(..., min_length=7)


class NoteTableResponse(BaseModel):
    id: int
    data: str
    date: datetime
    user_id: int
