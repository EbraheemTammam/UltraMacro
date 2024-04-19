from pydantic import BaseModel


class DivisionUploadResponse(BaseModel):
    department_1_id: int
    department_2_id: int
    name: str
    hours: int
    private: bool
    group: bool


class CourseUploadResponse(BaseModel):
    level: int
    semester: int
    division: str
    code: str
    required: bool  
    name: str
    lecture_hours: int 
    practical_hours: int
    credit_hours: int


class EnrollmentUploadResponse(BaseModel):
    seat_id: int
    student: str
    course: str
    code: str
    hours: int
    grade: str
    points: float
    mark: float
    full_mark: int