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
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from authentication.oauth2 import get_current_user
from database import get_db, get_async_db
import schemas.course as course_schemas
import models.course as course_models
import models.user as user_models
import handlers.course as course_handlers


course_router = APIRouter()

#	get all courses
@course_router.get(
	'',
    response_model=List[course_schemas.Course],
    status_code=status.HTTP_200_OK
)
async def get_courses(
	db: Annotated[AsyncSession, Depends(get_async_db)],
	user: Annotated[user_models.User, Depends(get_current_user)]
):
    return await course_handlers.get_all_courses(db)


#	create course
@course_router.post(
	'',
    response_model=course_schemas.Course,
    status_code=status.HTTP_201_CREATED
)
async def create_courses(
	course: course_schemas.CourseCreate,
	db: Annotated[AsyncSession, Depends(get_async_db)],
	user: Annotated[user_models.User, Depends(get_current_user)]
):
	return await course_handlers.create_course(course, db)


#	get one course
@course_router.get(
	'/{id}',
    response_model=course_schemas.Course | None,
    status_code=status.HTTP_200_OK
)
async def retreive_courses(
	id: Annotated[int, Path(..., title='id of course to be retrieved')],
	db: Annotated[AsyncSession, Depends(get_async_db)],
	user: Annotated[user_models.User, Depends(get_current_user)]
):
	return await course_handlers.get_one_course(id, db)


#	update course
@course_router.put(
	'/{id}',
    response_model=course_schemas.Course,
)
async def update_courses(
	id: Annotated[int, Path(..., title='id of course to be updated')],
	course: course_schemas.CourseCreate,
	db: Annotated[AsyncSession, Depends(get_async_db)],
	user: Annotated[user_models.User, Depends(get_current_user)]
):
	return await course_handlers.update_course(id, course, db)


#	delete course
@course_router.delete(
	'/{id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_courses(
	id: Annotated[int, Path(..., title='id of course to be updated')],
	db: Annotated[AsyncSession, Depends(get_async_db)],
	user: Annotated[user_models.User, Depends(get_current_user)]
):
	return await course_handlers.delete_course(id, db)
	