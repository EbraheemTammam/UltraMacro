from typing import List
from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete, and_
from sqlalchemy.orm import selectinload


from authentication.oauth2 import get_current_user
from database import get_async_db
from exceptions import CourseNotFoundException


import schemas.course as course_schemas
from models import (
    course as course_models,
    user as user_models,
    division as division_models
)



class CourseHandler:

    def __init__(self, user: user_models.User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)) -> None:
        self.user = user
        self.db = db
        self.NotFoundException = CourseNotFoundException()
        self.model = course_models.Course
        self.retrieve_query = (
            select(self.model).
            options(
                selectinload(self.model.divisions).
                options(
                    selectinload(division_models.Division.regulation),
                    selectinload(division_models.Division.department_1),
                    selectinload(division_models.Division.department_2),
                )
            )
        )
        if not user.is_admin:
            self.retrieve_query = self.retrieve_query.where(
                self.model.id.in_(
                    select(self.model.Divisions.columns.course_id).
                    where(
                        self.model.Divisions.columns.division_id.in_(
                            select(division_models.Division.id).
                            where(division_models.Division.users.any(id=user.id))
                        )
                    )
                )
            )


    async def get_all(self, regulation_id: int | None):
        courses = await self.db.execute(
            self.retrieve_query
            if not regulation_id else
            self.retrieve_query.where(
                self.model.id.in_(
                    select(division_models.CourseDivisions.columns.course_id).
                    where(
                        division_models.CourseDivisions.columns.division_id.in_(
                            select(division_models.Division.id).
                            where(division_models.Division.regulation_id==regulation_id)
                        )
                    )
                )
            )
        )
        return courses.scalars().all()


    async def create(self, course: course_schemas.CourseCreate):
        new_course = self.model(**course.dict(exclude={"divisions"}))
        self.db.add(new_course)
        if course.divisions:
            for d in course.divisions:
                division = await self.db.get(division_models.Division, d)
                new_course.divisions.append(division)
        await self.db.commit()
        await self.db.refresh(new_course)
        return await self.get_one(new_course.id)


    async def get_one(self, id: int):
        query = self.retrieve_query.where(self.model.id == id)
        course = await self.db.execute(query)
        course = course.scalar()
        if course:
            return course
        raise self.NotFoundException

    async def get_by_code(self, code: str):
        query = (
            select(self.model).
            where(self.model.code == code)
        )
        course = await self.db.execute(query)
        course = course.scalars().first()
        if course:
            return course
        raise self.NotFoundException


    async def get_by_code_and_divisions(self, code: str, divisions: List[division_models.Division]):
        query = (
            select(self.model).
            where(
                and_(
                    self.model.code == code,
                    self.model.divisions.any(d.id for d in divisions)
                )
            )
        )
        course = await self.db.execute(query)
        course = course.scalar()
        if course:
            return course
        raise self.NotFoundException


    async def update(self, id: int, course: course_schemas.CourseCreate):
        existing_course = await self.get_one(id)
        for key, value in course.dict(exclude={"divisions"}).items():
                setattr(existing_course, key, value)
        if course.divisions is not None:
            existing_course.divisions.clear()
            for division_id in course.divisions:
                division = await self.db.get(division_models.Division, division_id)
                if division:
                    existing_course.divisions.append(division)
        await self.db.commit()
        await self.db.refresh(existing_course)
        return existing_course


    async def delete(self, id: int):
        await self.get_one(id)
        await self.db.execute(
            delete(self.model).
            where(self.model.id == id)
        )
        await self.db.commit()
        return