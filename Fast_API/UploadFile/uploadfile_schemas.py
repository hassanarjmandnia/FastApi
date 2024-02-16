from pydantic import BaseModel, Field


class User(BaseModel):
    first_name: str = Field(..., min_length=4)
    last_name: str = Field(..., min_length=4)
    email: str = Field(..., min_length=8)
