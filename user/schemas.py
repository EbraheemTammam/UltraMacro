from uuid import UUID
from typing import List
from pydantic import BaseModel, EmailStr

from division.schemas import Division


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    is_admin: bool

class UserCreate(UserBase):
    password: str
    divisions: List[int]

class User(UserBase):
    id: UUID
    divisions: List[Division]

    class Config:
        from_attributes = True