from uuid import UUID
from typing import Annotated, List
from fastapi import (
	APIRouter,
	Response,
	status,
	Depends,
	Path,
	Query
)

import schemas.student as student_schemas
from handlers.student import StudentHandler

student_router = APIRouter()

#	get all students
@student_router.get(
	'',
    response_model=List[student_schemas.Student],
    status_code=status.HTTP_200_OK
)
async def get_students(
	handler: Annotated[StudentHandler, Depends(StudentHandler)],
	regulation: int = Query(None, title='id of regulation to filter result')
):
    return await handler.get_all(regulation)

#	get all graduate students
@student_router.get(
	'/graduates',
    response_model=List[student_schemas.Student],
    status_code=status.HTTP_200_OK
)
async def get_graduate_students(
	handler: Annotated[StudentHandler, Depends(StudentHandler)],
	regulation: int = Query(None, title='id of regulation to filter result')
):
    return await handler.get_all(regulation_id=regulation, graduate=True)


#	create student
@student_router.post(
	'',
    response_model=student_schemas.Student,
    status_code=status.HTTP_201_CREATED
)
async def create_students(
	student: student_schemas.StudentCreate,
	handler: Annotated[StudentHandler, Depends(StudentHandler)],
):
	return await handler.create(student)


#	get one student
@student_router.get(
	'/{id}',
    response_model=student_schemas.StudentDetail,
    status_code=status.HTTP_200_OK
)
async def retrieve_students(
	id: Annotated[UUID, Path(..., title='id of student to be retrieved')],
	handler: Annotated[StudentHandler, Depends(StudentHandler)],
):
	return await handler.get_student_detail(id)


#	update student
@student_router.put(
	'/{id}',
    response_model=student_schemas.Student,
)
async def update_students(
	id: Annotated[UUID, Path(..., title='id of student to be updated')],
	student: student_schemas.StudentCreate,
	handler: Annotated[StudentHandler, Depends(StudentHandler)],
):
	return await handler.update(id, student)


#	delete student
@student_router.delete(
	'/{id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_students(
	id: Annotated[UUID, Path(..., title='id of student to be updated')],
	handler: Annotated[StudentHandler, Depends(StudentHandler)],
):
	return await handler.delete(id)