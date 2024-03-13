from typing import List
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete, and_
from sqlalchemy.orm import selectinload


import schemas.course as course_schemas
from models import (
    course as course_models,
    user as user_models,
    division as division_models
)




async def get_all_courses(regulation_id: int | None, user: user_models.User, db: AsyncSession):
    query = (
        select(course_models.Course).
        options(
            selectinload(course_models.Course.divisions).
            options(
                selectinload(division_models.Division.regulation),
                selectinload(division_models.Division.department_1),
                selectinload(division_models.Division.department_2),
            )
        )
    )
    if not user.is_admin:
        query = query.where(
            course_models.Course.id.in_(
                select(course_models.CourseDivisions.columns.course_id).
                where(
                    course_models.CourseDivisions.columns.division_id.in_(
                        select(division_models.Division.id).
                        where(division_models.Division.users.any(id=user.id))
                    )
                )
            )
        )
    if regulation_id:
        query = query.where(
            course_models.Course.id.in_(
                select(course_models.CourseDivisions.columns.course_id).
                where(
                    course_models.CourseDivisions.columns.division_id.in_(
                        select(division_models.Division.id).
                        where(division_models.Division.regulation_id==regulation_id)
                    )
                )
            )
        )
    courses = await db.execute(query)
    return courses.scalars().all()


async def create_course(course: course_schemas.CourseCreate, db: AsyncSession):
    new_course = course_models.Course(**course.dict(exclude={"divisions"}))
    db.add(new_course)
    if course.divisions:
        for d in course.divisions:
            division = await db.get(division_models.Division, d)
            new_course.divisions.append(division)
    await db.commit()
    await db.refresh(new_course)
    return await get_one_course(new_course.id, db)
    # query = await db.execute(
    # 	insert(course_models.Course).
    # 	values({key: value for key, value in course.items() if key != "divisions"}).
    # 	returning(course_models.Course)
    # )
    # course = query.scalar_one()
    # for d in course.divisions:
    #     await db.execute(
    #         insert(course_models.CourseDivisions).
    #         values({'course_id': course.id, 'division_id': d})
    #     )
    # await db.commit()
    # await db.refresh(course)
    # return course


async def get_one_course(id: int, db: AsyncSession):
    query = (
    	select(course_models.Course).
        where(course_models.Course.id == id).
        options(
            selectinload(course_models.Course.divisions).
            options(
                selectinload(division_models.Division.regulation),
                selectinload(division_models.Division.department_1),
                selectinload(division_models.Division.department_2),
            )
        )
    )
    course = await db.execute(query)
    course = course.scalar()
    if course:
        return course
    raise HTTPException(
    	detail=f"no course with given id: {id}",
    	status_code=status.HTTP_404_NOT_FOUND
    )


async def get_course_by_code(code: str, db: AsyncSession):
    query = (
    	select(course_models.Course).
        where(course_models.Course.code == code)
    )
    course = await db.execute(query)
    course = course.scalars().first()
    if course:
        return course
    raise HTTPException(
    	detail=f"no course with given code: {code}",
    	status_code=status.HTTP_404_NOT_FOUND
    )


async def get_course_by_code_and_divisions(code: str, divisions: List[division_models.Division], db: AsyncSession):
    query = (
    	select(course_models.Course).
        where(
            and_(
                course_models.Course.code == code,
                course_models.Course.divisions.any(d.id for d in divisions)
            )
        )
    )
    course = await db.execute(query)
    course = course.scalar()
    if course:
        return course
    raise HTTPException(
    	detail=f"no course with given code or divisions: {code}",
    	status_code=status.HTTP_404_NOT_FOUND
    )

async def update_course(id: int, course: course_schemas.CourseCreate, db: AsyncSession):
    existing_course = await get_one_course(id, db)
    for key, value in course.dict(exclude={"divisions"}).items():
            setattr(existing_course, key, value)
    if course.divisions is not None:
        existing_course.divisions.clear()
        for division_id in course.divisions:
            division = await db.get(division_models.Division, division_id)
            if division:
                existing_course.divisions.append(division)
    await db.commit()
    await db.refresh(existing_course)
    return existing_course
    # query = (
    # 	update(course_models.Course).
    #     where(course_models.Course.id == id).
    #     values({key: value for key, value in course.items() if key != "divisions"}).
    #     returning(course_models.Course)
    # )
    # query = await db.execute(query)
    # course = query.scalar()
    # if not course:
    #     raise HTTPException(
    #     detail=f"no course with given id: {id}",
    #     status_code=status.HTTP_404_NOT_FOUND
    # )
    # await db.commit()
    # await db.refresh(course)
    # return course


async def delete_course(id: int, db: AsyncSession):
    await get_one_course(id, db)
    await db.execute(
    	delete(course_models.Course).
        where(course_models.Course.id == id)
    )
    await db.commit()
    return