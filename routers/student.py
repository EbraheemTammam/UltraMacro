from uuid import UUID
from typing import Annotated, List
from fastapi import (
	APIRouter,
	Response,
	status,
	HTTPException,
	Depends,
	Path,
	Query
)
from sqlalchemy import insert, update, delete
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from authentication.oauth2 import get_current_user
from authentication.permissions import has_permission
from database import get_db, get_async_db
import schemas.student as student_schemas
from models import (
	user as user_models,
	student as student_models,
	division as division_models
)
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
async def retreive_students(
	id: Annotated[UUID, Path(..., title='id of student to be retrieved')],
	handler: Annotated[StudentHandler, Depends(StudentHandler)],
):
	#await has_permission(user=user, class_=student_models.Student, object_id=id, db=db)
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
	#await has_permission(user=user, class_=student_models.Student, object_id=id, db=db)
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
	#await has_permission(user=user, class_=student_models.Student, object_id=id, db=db)
	return await handler.delete(id)