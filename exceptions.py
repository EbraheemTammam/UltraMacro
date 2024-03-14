from typing import Any, Dict
from typing_extensions import Annotated, Doc
from fastapi import HTTPException, status




class NotFoundException(HTTPException):

    def __init__(self, detail: Any = None) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, detail)



class RegulationNotFoundException(NotFoundException):

    def __init__(self) -> None:
        detail = 'Regulation not found'
        super().__init__(detail)



class DivisionNotFoundException(NotFoundException):

    def __init__(self) -> None:
        detail = 'Division not found'
        super().__init__(detail)



class DepartmentNotFoundException(NotFoundException):

    def __init__(self) -> None:
        detail = 'Department not found'
        super().__init__(detail)



class CourseNotFoundException(NotFoundException):

    def __init__(self) -> None:
        detail = 'Course not found'
        super().__init__(detail)



class UserNotFoundException(NotFoundException):

    def __init__(self) -> None:
        detail = 'User not found'
        super().__init__(detail)



class EnrollmentNotFoundException(NotFoundException):

    def __init__(self) -> None:
        detail = 'Enrollment not found'
        super().__init__(detail)



class StudentNotFoundException(NotFoundException):

    def __init__(self) -> None:
        detail = 'Student not found'
        super().__init__(detail)