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
from database import get_db, get_async_db
import schemas.student as student_schemas
from models import (
	user as user_models,
	student as student_models,
	division as division_models
)
import handlers.student as student_handlers

student_router = APIRouter()

#	get all students
@student_router.get(
	'',
    response_model=List[student_schemas.Student],
    status_code=status.HTTP_200_OK
)
async def get_students(
	db: Annotated[AsyncSession, Depends(get_async_db)],
	user: Annotated[user_models.User, Depends(get_current_user)]
):
    return await student_handlers.get_all_students(db)

#	get all graduate students
@student_router.get(
	'/graduates',
    response_model=List[student_schemas.Student],
    status_code=status.HTTP_200_OK
)
async def get_graduate_students(
	db: Annotated[AsyncSession, Depends(get_async_db)],
	user: Annotated[user_models.User, Depends(get_current_user)]
):
    return await student_handlers.get_all_students(db=db, graduate=True)


#	create student
@student_router.post(
	'',
    response_model=student_schemas.Student,
    status_code=status.HTTP_201_CREATED
)
async def create_students(
	student: student_schemas.StudentCreate,
	db: Annotated[AsyncSession, Depends(get_async_db)],
	user: Annotated[user_models.User, Depends(get_current_user)]
):
	return await student_handlers.create_student(student, db)


#	get one student
@student_router.get(
	'/{id}',
    response_model=student_schemas.Student | None,
    status_code=status.HTTP_200_OK
)
async def retreive_students(
	id: Annotated[UUID, Path(..., title='id of student to be retrieved')],
	db: Annotated[AsyncSession, Depends(get_async_db)],
	user: Annotated[user_models.User, Depends(get_current_user)]
):
	return await student_handlers.get_one_student(id, db)


#	update student
@student_router.put(
	'/{id}',
    response_model=student_schemas.Student,
)
async def update_students(
	id: Annotated[UUID, Path(..., title='id of student to be updated')],
	student: student_schemas.StudentCreate,
	db: Annotated[AsyncSession, Depends(get_async_db)],
	user: Annotated[user_models.User, Depends(get_current_user)]
):
	return await student_handlers.update_student(id, student, db)


#	delete student
@student_router.delete(
	'/{id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_students(
	id: Annotated[UUID, Path(..., title='id of student to be updated')],
	db: Annotated[AsyncSession, Depends(get_async_db)],
	user: Annotated[user_models.User, Depends(get_current_user)]
):
	return await student_handlers.delete_student(id, db)