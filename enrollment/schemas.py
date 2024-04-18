from uuid import UUID
from typing import Annotated, List, Optional
from pydantic import BaseModel

from course.schemas import CourseBase


class EnrollmentBase(BaseModel):
    seat_id: int
    level: int
    semester: int
    year: int
    month: str
    points: float
    mark: int
    full_mark: int
    grade: str


class EnrollmentCreate(EnrollmentBase):
    student_id: UUID
    course_id: int


class EnrollmentPartialUpdate(BaseModel):
    mark: Optional[float]
    grade: Optional[str]
    points: Optional[float]


class Enrollment(EnrollmentBase):
    id: UUID
    course: CourseBase

    class Config:
        from_attributes = True


class Semester(BaseModel):
    level: int
    semester: int
    points: float | None
    enrollments: List[Enrollment]

    class Config:
        from_attributes = True