from pydantic import BaseModel, Field
from datetime import datetime


class RoleTableAdd(BaseModel):
    name: str = Field(..., min_length=4)


