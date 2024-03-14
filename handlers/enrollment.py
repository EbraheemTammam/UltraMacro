from typing import Optional
from uuid import UUID
from fastapi import HTTPException, status, Depends
from sqlalchemy import String, cast, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete
from sqlalchemy.orm import selectinload


from authentication.oauth2 import get_current_user
from database import get_async_db
from exceptions import EnrollmentNotFoundException


import schemas.enrollment as enrollment_schemas
from models import (
	course as course_models,
	enrollment as enrollment_models,
	student as student_models,
	user as user_models
)
from handlers import (
	student as student_handlers,
	course as course_handlers
)



class EnrollmentHandler:


	def __init__(
		self, 
		user: user_models.User = Depends(get_current_user), 
		db: AsyncSession = Depends(get_async_db),
	) -> None:
		self.user = user
		self.db = db
		self.model = enrollment_models.Enrollment
		self.NotFoundException = EnrollmentNotFoundException()
		self.retrieve_query = (
			select(self.model).
			options(
				selectinload(self.model.course)
			)
		)

	
	async def get_all(
		self,
		student_id: Optional[UUID], 
		level: Optional[int], 
		semester: Optional[int],
		course_id: Optional[int],
		execuse: bool = True
	):
		query = self.retrieve_query
		if not execuse:
			query = query.where(self.model.grade!='عذر')
		if student_id:
			query = query.where(self.model.student_id==cast(str(student_id), String))
		if level:
			query = query.where(
				self.model.course_id.in_(
					select(course_models.Course.id).
					where(course_models.Course.level==level)
				)
			)
		if semester:
			query = query.where(
				self.model.course_id.in_(
					select(course_models.Course.id).
					where(course_models.Course.semester==semester)
				)
			)
		if course_id:
			query = query.where(self.model.course_id==course_id)
		result = await self.db.execute(query)
		enrollments = result.scalars().all()
		return enrollments


	async def create(self, enrollment: enrollment_schemas.EnrollmentCreate):
		student = await self.db.get(student_models.Student, enrollment.student_id)
		if not student:
			raise HTTPException(
				detail='Student not found',
				status_code=status.HTTP_400_BAD_REQUEST
			)
		course = await self.db.get(course_models.Course, enrollment.course_id)
		if not course:
			raise HTTPException(
				detail='Course not found',
				status_code=status.HTTP_400_BAD_REQUEST
			)
		new_enrollment = self.model(**enrollment.dict())
		self.db.add(new_enrollment)
		await self.db.commit()
		await self.db.refresh(new_enrollment)
		return new_enrollment


	async def get_one(self, id: UUID):
		enrollment = await self.db.get(self.model, id)
		if enrollment:
			return enrollment
		raise self.NotFoundException


	async def get_or_create(
		self,
		headers: dict, 
		enrollment: dict, 
		student: student_models.Student, 
		course: course_models.Course,
	):
		#	check if enrollment exists
		query = (
			select(self.model).
			where(
				and_(
					self.model.seat_id==enrollment.get('seat_id'),
					self.model.level==headers.get('level'),
					self.model.semester==headers.get('semester'),
					self.model.year==headers.get('year'),
					self.model.month==headers.get('month'),
					self.model.mark==enrollment.get('mark'),
					self.model.student_id==student.id,
					self.model.course_id==course.id,
				)
			)
		)
		result = await self.db.execute(query)
		existing_enrollment = result.scalar()
		if existing_enrollment:
			return None
		#	if not, create one
		new_enrollment = self.model(
			**{
				'seat_id': enrollment['seat_id'],
				'level': headers['level'],
				'semester': headers['semester'],
				'year': headers['year'],
				'month': headers['month'],
				'mark': enrollment['mark'],
				'full_mark': enrollment['full_mark'],
				'grade': enrollment['grade'],
				'points': (
					(int(enrollment['mark']) / (course.credit_hours * 10)) - 5 
					if enrollment['grade'] in ['A', 'B', 'C', 'D'] and course.credit_hours != 0
					else 0
				),
				'student_id': student.id,
				'course_id': course.id,
			}
		)
		return new_enrollment


	async def update(self, id: UUID, enrollment: enrollment_schemas.EnrollmentCreate):
		existing_enrollment = self.get_one(id)
		for key, val in enrollment.dict().items():
			setattr(existing_enrollment, key, val)
		await self.db.commit()
		await self.db.refresh(existing_enrollment)
		return existing_enrollment


	async def delete(self, id: UUID):
		enrollment = await self.get_one9id
		await self.db.delete(enrollment)
		await self.db.commit()
		return

