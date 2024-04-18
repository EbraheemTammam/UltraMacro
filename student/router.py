from uuid import UUID
from typing import Annotated, List
from fastapi import (
	APIRouter,
	status,
	Depends,
	Path,
	Query
)

from generics.permissions import StudentPermission

from .schemas import StudentCreate, StudentDetail, Student
from .handler import StudentHandler

student_router = APIRouter()

#	get all students
@student_router.get(
	'',
    response_model=List[Student],
    status_code=status.HTTP_200_OK
)
async def get_students(
	permission_class: Annotated[StudentPermission, Depends(StudentPermission)],
	regulation: int = Query(None, title='id of regulation to filter result')
):
	handler = StudentHandler(permission_class.user, permission_class.db)
	return await handler.get_all(regulation)

#	get all graduate students
@student_router.get(
	'/graduates',
    response_model=List[Student],
    status_code=status.HTTP_200_OK
)
async def get_graduate_students(
	permission_class: Annotated[StudentPermission, Depends(StudentPermission)],
	regulation: int = Query(None, title='id of regulation to filter result')
):
	handler = StudentHandler(permission_class.user, permission_class.db)
	return await handler.get_all(regulation_id=regulation, graduate=True)


#	create student
@student_router.post(
	'',
    response_model=Student,
    status_code=status.HTTP_201_CREATED
)
async def create_students(
	student: StudentCreate,
	permission_class: Annotated[StudentPermission, Depends(StudentPermission)]
):
	handler = StudentHandler(permission_class.user, permission_class.db)
	return await handler.create(student)


#	get one student
@student_router.get(
	'/{id}',
    response_model=StudentDetail,
    status_code=status.HTTP_200_OK
)
async def retrieve_students(
	id: Annotated[UUID, Path(..., title='id of student to be retrieved')],
	permission_class: Annotated[StudentPermission, Depends(StudentPermission)]
):
	await permission_class.check_permission(id)
	handler = StudentHandler(permission_class.user, permission_class.db)
	return await handler.get_student_detail(id)


#	update student
@student_router.put(
	'/{id}',
    response_model=Student,
)
async def update_students(
	id: Annotated[UUID, Path(..., title='id of student to be updated')],
	student: StudentCreate,
	permission_class: Annotated[StudentPermission, Depends(StudentPermission)]
):
	await permission_class.check_permission(id)
	handler = StudentHandler(permission_class.user, permission_class.db)
	return await handler.update(id, student)


#	delete student
@student_router.delete(
	'/{id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_students(
	id: Annotated[UUID, Path(..., title='id of student to be updated')],
	permission_class: Annotated[StudentPermission, Depends(StudentPermission)]
):
	await permission_class.check_permission(id)
	handler = StudentHandler(permission_class.user, permission_class.db)
	await handler.get_one(id)
	return await handler.delete(id)