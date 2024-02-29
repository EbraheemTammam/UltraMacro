from typing import Annotated
from pydantic import BaseModel
from schemas.regulation import Regulation
from schemas.department import Department


class DivisionBase(BaseModel):
    name: str
    hours: int
    private: bool
    group: bool

class DivisionCreate(DivisionBase):
    regulation_id: int
    department_1_id: int | None
    department_2_id: int | None

class Division(DivisionBase):
    id: int
    regulation: Regulation
    department_1: Department | None
    department_2: Department | None

    class Config:
        from_attributes = True