from typing import Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import String, cast, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete
from sqlalchemy.orm import selectinload

import schemas.enrollment as enrollment_schemas
from models import (
	course as course_models,
	enrollment as enrollment_models,
	student as student_models
)
from handlers import (
	student as student_handlers,
	course as course_handlers
)




async def get_all_enrollments(
	student_id: Optional[UUID], 
	level: Optional[int], 
	semester: Optional[int],
	course_id: Optional[int],
	db: AsyncSession,
	execuse: bool = True
):
	query = select(enrollment_models.Enrollment).options(selectinload(enrollment_models.Enrollment.course))
	if not execuse:
		query = query.where(enrollment_models.Enrollment.grade!='عذر')
	if student_id:
		query = query.where(enrollment_models.Enrollment.student_id==cast(str(student_id), String))
	if level:
		query = query.where(
			enrollment_models.Enrollment.course_id.in_(
				select(course_models.Course.id).
				where(course_models.Course.level==level)
			)
		)
	if semester:
		query = query.where(
			enrollment_models.Enrollment.course_id.in_(
				select(course_models.Course.id).
				where(course_models.Course.semester==semester)
			)
		)
	if course_id:
		query = query.where(enrollment_models.Enrollment.course_id==course_id)
	result = await db.execute(query)
	enrollments = result.scalars().all()
	return enrollments


async def create_enrollment(enrollment: enrollment_schemas.EnrollmentCreate, db: AsyncSession):
	await student_handlers.get_one_student(enrollment.student_id, db)
	await course_handlers.get_one_course(enrollment.course_id, db)
	new_enrollment = enrollment_models.Enrollment(**enrollment.dict())
	db.add(new_enrollment)
	await db.commit()
	await db.refresh(new_enrollment)
	return new_enrollment


async def get_one_enrollment(id: UUID, db: AsyncSession):
	enrollment = await db.get(enrollment_models, id)
	if enrollment:
		return enrollment
	raise HTTPException(
		detail=f'no enrollment with given id: {id}',
		status_code=status.HTTP_404_NOT_FOUND
	)


async def enrollment_get_or_create(
	headers: dict, 
	enrollment: dict, 
	student: student_models.Student, 
	course: course_models.Course,
	db: AsyncSession
):
	query = (
		select(enrollment_models.Enrollment).
		where(
			and_(
				enrollment_models.Enrollment.seat_id==enrollment.get('seat_id'),
				enrollment_models.Enrollment.level==headers.get('level'),
				enrollment_models.Enrollment.semester==headers.get('semester'),
				enrollment_models.Enrollment.year==headers.get('year'),
				enrollment_models.Enrollment.month==headers.get('month'),
				enrollment_models.Enrollment.mark==enrollment.get('mark'),
				enrollment_models.Enrollment.student_id==student.id,
				enrollment_models.Enrollment.course_id==course.id,
			)
		)
	)
	result = await db.execute(query)
	existing_enrollment = result.scalar()
	if existing_enrollment:
		return None
	new_enrollment = enrollment_models.Enrollment(
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


async def update_enrollment(id: UUID, enrollment: enrollment_schemas.EnrollmentCreate, db: AsyncSession):
	existing_enrollment = get_one_enrollment(id, db)
	for key, val in enrollment.dict().items():
		setattr(existing_enrollment, key, val)
	await db.commit()
	await db.refresh(existing_enrollment)
	return existing_enrollment


async def delete_enrollment(id: UUID, db: AsyncSession):
	enrollment = await get_one_enrollment(id, db)
	await db.delete(enrollment)
	await db.commit()
	return

