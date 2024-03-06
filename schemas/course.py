from typing import Annotated
from pydantic import BaseModel


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
    pass

class Course(CourseBase):
    id: int

    class Config:
        from_attributes = True