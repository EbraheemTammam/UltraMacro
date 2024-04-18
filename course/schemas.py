from typing import Annotated, List
from pydantic import BaseModel

from division.schemas import Division


class CourseBase(BaseModel):
    code: str
    name: str
    lecture_hours: int
    practical_hours: int
    credit_hours: int
    level: int
    semester: int
    required: bool


class CourseCreate(CourseBase):
    divisions: List[int]

class Course(CourseBase):
    id: int
    divisions: List[Division]

    class Config:
        from_attributes = True