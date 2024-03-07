from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete
from sqlalchemy.orm import selectinload


import schemas.course as course_schemas
from models import (
    course as course_models,
    user as user_models
)




async def get_all_courses(user: user_models.User, db: AsyncSession):
    query = select(course_models.Course)
    if not user.is_admin:
        query = query.where(course_models.Course.divisions in user.divisions)
    courses = await db.execute(query)
    return courses.scalars().all()


async def create_course(course: course_schemas.CourseCreate, db: AsyncSession):
    query = await db.execute(
    	insert(course_models.Course).
    	values(**course.dict()).
    	returning(course_models.Course)
    )
    course = query.scalar_one()
    await db.commit()
    await db.refresh(course)
    return course


async def get_one_course(id: int, user: user_models.User, db: AsyncSession):
    query = (
    	select(course_models.Course).
        where(course_models.Course.id == id)
    )
    if not user.is_admin:
        query = query.where(course_models.Course.divisions in user.divisions)
    course = await db.execute(query)
    course = course.scalar()
    if course:
        return course
    raise HTTPException(
    	detail="no course with given id",
    	status_code=status.HTTP_404_NOT_FOUND
    )


async def update_course(id: int, course: course_schemas.CourseCreate, user: user_models.User, db: AsyncSession):
    query = (
    	update(course_models.Course).
        where(course_models.Course.id == id).
        values({**course.dict()}).
        returning(course_models.Course)
    )
    if not user.is_admin:
        query = query.where(course_models.Course.divisions in user.divisions)
    query = await db.execute(query)
    course = query.scalar()
    if not course:
        raise HTTPException(
        detail=f"no course with given id: {id}",
        status_code=status.HTTP_404_NOT_FOUND
    )
    await db.commit()
    await db.refresh(course)
    return course


async def delete_course(id: int, user: user_models.User, db: AsyncSession):
    await get_one_course(id, user, db)
    await db.execute(
    	delete(course_models.Course).
        where(course_models.Course.id == id)
    )
    await db.commit()
    return