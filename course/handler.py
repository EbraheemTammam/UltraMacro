from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, and_
from sqlalchemy.orm import selectinload


from generics.exceptions import CourseNotFoundException


from .schemas import CourseCreate
from .models import Course, CourseDivisions

from division.models import Division
from enrollment.models import Enrollment
from user.models import User



class CourseHandler:

    def __init__(self, user: User, db: AsyncSession) -> None:
        self.user = user
        self.db = db
        self.NotFoundException = CourseNotFoundException()
        self.retrieve_query = (
            select(Course).
            options(
                selectinload(Course.divisions).
                options(
                    selectinload(Division.regulation),
                    selectinload(Division.department_1),
                    selectinload(Division.department_2),
                )
            )
        )
        if not self.user.is_admin:
            self.retrieve_query = self.retrieve_query.where(
                Course.id.in_(
                    select(CourseDivisions.columns.course_id).
                    where(
                        CourseDivisions.columns.division_id.in_(
                            select(Division.id).
                            where(Division.users.any(id=self.user.id))
                        )
                    )
                )
            )


    async def get_all(self, regulation_id: int | None):
        courses = await self.db.execute(
            self.retrieve_query
            if not regulation_id else
            self.retrieve_query.where(
                Course.id.in_(
                    select(CourseDivisions.columns.course_id).
                    where(
                        CourseDivisions.columns.division_id.in_(
                            select(Division.id).
                            where(Division.regulation_id==regulation_id)
                        )
                    )
                )
            )
        )
        return courses.scalars().all()


    async def create(self, course: CourseCreate):
        new_course = Course(**course.dict(exclude={"divisions"}))
        self.db.add(new_course)
        if course.divisions:
            for d in course.divisions:
                division = await self.db.get(Division, d)
                new_course.divisions.append(division)
        await self.db.commit()
        await self.db.refresh(new_course)
        return await self.get_one(new_course.id)


    async def get_one(self, id: int):
        query = self.retrieve_query.where(Course.id == id)
        course = await self.db.execute(query)
        course = course.scalar()
        if course:
            return course
        raise self.NotFoundException


    async def get_by_code_and_division_or_none(self, code: str, division_id: int):
        #   try to get by code and division
        query = await self.db.execute(
            select(Course).
            where(
                and_(
                    Course.code == code,
                    Course.divisions.any(id=division_id)
                )
            )
        )
        course = query.scalar()
        #   if not exists try to get by code only
        if not course:
            query = await self.db.execute(select(Course).where(Course.code == code))
            course = query.scalars().first()    
        #   return if exists
        if course:
            return course
    

    async def check_required_and_not_passed(self, division_id: int, passed_enrollments: List[Enrollment]):
        passed_courses_query = await self.db.execute(
			select(Course.id).
			where(
				Course.id.in_([e.course_id for e in passed_enrollments])
			)
		)
        passed_courses = passed_courses_query.scalars().all()
        required_courses = await self.db.execute(
			select(Course).
			where(
				and_(
					Course.required==True,
					Course.divisions.any(id=division_id)
				)
			).
			except_(Course.id.in_(passed_courses)).
            exists()
		)
        return required_courses


    async def update(self, id: int, course: CourseCreate):
        existing_course = await self.get_one(id)
        for key, value in course.dict(exclude={"divisions"}).items():
                setattr(existing_course, key, value)
        if course.divisions is not None:
            existing_course.divisions.clear()
            for division_id in course.divisions:
                division = await self.db.get(Division, division_id)
                if division:
                    existing_course.divisions.append(division)
        await self.db.commit()
        await self.db.refresh(existing_course)
        return existing_course


    async def delete(self, id: int):
        await self.db.execute(
            delete(Course).
            where(Course.id == id)
        )
        await self.db.commit()
        return