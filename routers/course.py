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
    query = await db.execute(
        select(course_models.Course)
	)
    return query.scalars().all()


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
	query = await db.execute(
		insert(course_models.Course).
		values(**course.dict()).
		returning(course_models.Course)
	)
	course = query.scalar_one()
	await db.commit()
	await db.refresh(course)
	return course


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
	query = await db.execute(
		select(course_models.Course).where(
			course_models.Course.id == id
		)
	)
	course = query.scalar()
	if course:
		return course
	raise HTTPException(
		detail="no course with given id",
		status_code=status.HTTP_404_NOT_FOUND
	)


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
	query = await db.execute(
		update(course_models.Course).
        where(course_models.Course.id == id).
        values({**course.dict()}).
        returning(course_models.Course)
	)
	course = query.scalar()
	if not course:
		raise HTTPException(
		detail="no course with given id",
		status_code=status.HTTP_404_NOT_FOUND
	)
	await db.commit()
	await db.refresh(course)
	return course


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
	query = await db.execute(
		select(course_models.Course).where(
			course_models.Course.id == id
		)
	)
	if not query.scalar():
		raise HTTPException(
			detail="no course with given id",
			status_code=status.HTTP_404_NOT_FOUND
		)
	query = await db.execute(
		delete(course_models.Course).
        where(course_models.Course.id == id)
	)
	await db.commit()
	return