from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel

from division.schemas import Division
from enrollment.schemas import Semester


class StudentBase(BaseModel):
    name: str
    level: int
    registered_hours: int
    passed_hours: int
    excluded_hours: int
    research_hours: int
    total_points: float
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
    total_points: Optional[float] = 0
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


class StudentDetail(StudentBase):
    regulation: str | None
    department_1: str | None
    department_2: str | None
    group: str
    division: str | None
    id: UUID
    details: List[Semester]