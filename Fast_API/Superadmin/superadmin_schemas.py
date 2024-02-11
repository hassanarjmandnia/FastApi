from pydantic import BaseModel, Field


class RoleTableAdd(BaseModel):
    name: str = Field(..., min_length=4)


class UserRoleUpdate(BaseModel):
    name: str = Field(..., min_length=4)
    user_id: int = Field(...)


class UserStatusUpdate(BaseModel):
    user_id: int = Field(...)
    new_status: bool = Field(...)
