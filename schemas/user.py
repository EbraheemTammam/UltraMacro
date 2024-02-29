from uuid import UUID
from typing import Annotated
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    is_admin: bool

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: UUID

    class Config:
        from_attributes = True