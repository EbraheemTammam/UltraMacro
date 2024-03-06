from uuid import UUID
from typing import Optional
from pydantic import BaseModel

from schemas.division import Division



class StudentBase(BaseModel):
    name: str
    level: int
    registered_hours: int
    passed_hours: int
    excluded_hours: int
    research_hours: int
    gpa: float
    total_mark: float
    graduate: bool

class StudentCreate(StudentBase):
    group_id: int
    division_id: int | None
    level: Optional[int] = 1
    registered_hours: Optional[int] = 0
    passed_hours: Optional[int] = 0
    excluded_hours: Optional[int] = 0
    research_hours: Optional[int] = 0
    gpa: Optional[float] = 0
    total_mark: Optional[float] = 0
    graduate: Optional[bool] = False

class Student(StudentBase):
    id: UUID
    group: Division
    division: Division | None

    class Config:
        from_attributes = True

class GrduateStudent(Student):
    semester: int
    year: int