from typing import Optional
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
    department_1_id: Optional[int] | None
    department_2_id: Optional[int] | None

class Division(DivisionBase):
    id: int
    regulation: Regulation
    department_1: Department | None
    department_2: Department | None

    class Config:
        from_attributes = True