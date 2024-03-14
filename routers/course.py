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
from authentication.permissions import has_permission
from database import get_db, get_async_db
import schemas.course as course_schemas
import models.course as course_models
import models.user as user_models
from handlers.course import CourseHandler


course_router = APIRouter()

#	get all courses
@course_router.get(
	'',
    response_model=List[course_schemas.Course],
    status_code=status.HTTP_200_OK
)
async def get_courses(
	handler: Annotated[CourseHandler, Depends(CourseHandler)],
	regulation: int = Query(None, title='id of regulation to filter result')
):
    return await handler.get_all(regulation)


#	create course
@course_router.post(
	'',
    response_model=course_schemas.Course,
    status_code=status.HTTP_201_CREATED
)
async def create_courses(
	course: course_schemas.CourseCreate,
	handler: Annotated[CourseHandler, Depends(CourseHandler)],
):
	return await handler.create(course)


#	get one course
@course_router.get(
	'/{id}',
    response_model=course_schemas.Course,
    status_code=status.HTTP_200_OK
)
async def retreive_courses(
	id: Annotated[int, Path(..., title='id of course to be retrieved')],
	handler: Annotated[CourseHandler, Depends(CourseHandler)],
):
	#await has_permission(user=user, class_=course_models.Course, object_id=id, db=db)
	return await handler.get_one(id)


#	update course
@course_router.put(
	'/{id}',
    response_model=course_schemas.Course,
)
async def update_courses(
	id: Annotated[int, Path(..., title='id of course to be updated')],
	course: course_schemas.CourseCreate,
	handler: Annotated[CourseHandler, Depends(CourseHandler)],
):
	#await has_permission(user=user, class_=course_models.Course, object_id=id, db=db)
	return await handler.update(id, course)


#	delete course
@course_router.delete(
	'/{id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_courses(
	id: Annotated[int, Path(..., title='id of course to be updated')],
	handler: Annotated[CourseHandler, Depends(CourseHandler)],
):
	#await has_permission(user=user, class_=course_models.Course, object_id=id, db=db)
	return await handler.delete(id)
	