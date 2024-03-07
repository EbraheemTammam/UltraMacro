from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete
from sqlalchemy.orm import selectinload


import schemas.course as course_schemas
import models.course as course_models




async def get_all_courses(db: AsyncSession):
    query = await db.execute(
        select(course_models.Course)
	)
    return query.scalars().all()


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


async def get_one_course(id: int, db: AsyncSession):
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


async def update_course(id: int, course: course_schemas.CourseCreate, db: AsyncSession):
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


async def delete_course(id: int, db: AsyncSession):
    await get_one_course(id, db)
    await db.execute(
    	delete(course_models.Course).
        where(course_models.Course.id == id)
    )
    await db.commit()
    return