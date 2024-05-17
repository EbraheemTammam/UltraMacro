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
    student: str
    course: str
    status: str