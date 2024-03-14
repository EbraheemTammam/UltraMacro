from typing import Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import or_, and_, func, String, cast
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete, String
from sqlalchemy.orm import selectinload

import schemas.student as student_schemas
from models import (
	student as student_models,
	division as division_models,
	user as user_models,
	enrollment as enrollment_models,
	course as course_models
)
from handlers import (
    division as division_handlers,
    enrollment as enrollment_handlers
)


async def get_semester_detail(
	student_id: Optional[UUID], 
	level: Optional[int], 
	semester: Optional[int],
	db: AsyncSession
):
	enrollments = await enrollment_handlers.get_all_enrollments(student_id, level, semester, None, db)
	total_points_query = (
		select(func.sum(enrollment_models.Enrollment.points * course_models.Course.credit_hours)).
		join(course_models.Course).
		where(
			and_(
				enrollment_models.Enrollment.grade.in_(['A', 'B', 'C', 'D']),
				enrollment_models.Enrollment.student_id==cast(str(student_id), String),
				enrollment_models.Enrollment.course_id.in_(
					select(course_models.Course.id).
					where(
						and_(
							course_models.Course.level==level,
							course_models.Course.semester==semester
						)
					)
				)
			)
		)
	)
	result = await db.execute(total_points_query)
	points = result.scalar()
	return {'level': level, 'semester': semester, 'points': points, 'enrollments': enrollments}


async def get_student_detail(id: UUID, db: AsyncSession):
	student = await get_one_student(id, db)
	details = [await get_semester_detail(id, l, s, db) for l in range(1, 5) for s in range(1, 4)]
	return {
		'regulation': student.division.regulation.name if student.division else student.group.regulation.name,
		'department_1': (
			student.division.department_1.name 
			if student.division and student.division.department_1
			else (
				student.group.department_1.name
				if student.group.department_1
				else None
			)
		),
		'department_2': (
			student.division.department_2.name 
			if student.division and student.division.department_2
			else (
				student.group.department_2.name
				if student.group.department_2
				else None
			)
		),
		'group': student.group.name,
		'division': student.division.name if student.division else None,
		**{key: val for key, val in student.__dict__.items() if key not in ['group', 'division']}, 
		'details': details
	}


def main_query():
	return (
		select(student_models.Student).
		options(
			selectinload(student_models.Student.group).
			options(
				selectinload(division_models.Division.regulation),
				selectinload(division_models.Division.department_1),
				selectinload(division_models.Division.department_2),
			),
			selectinload(student_models.Student.division).
			options(
				selectinload(division_models.Division.regulation),
				selectinload(division_models.Division.department_1),
				selectinload(division_models.Division.department_2),
			)
		)
	)


async def get_all_students(regulation_id: int | None, user: user_models.User, db: AsyncSession, graduate: bool = False):
	query = main_query()
	if not user.is_admin:
		query = query.where(
			or_(
				student_models.Student.division_id.in_(
					select(division_models.Division.id).
					where(division_models.Division.users.any(id=user.id))
				),
				student_models.Student.group_id.in_(
					select(division_models.Division.id).
					where(division_models.Division.users.any(id=user.id))
				)
			)
		)
	if regulation_id:
		query = query.where(
			or_(
				student_models.Student.group_id.in_(
					select(division_models.Division.id).
					where(division_models.Division.regulation_id==regulation_id)
				),
				student_models.Student.division_id.in_(
					select(division_models.Division.id).
					where(division_models.Division.regulation_id==regulation_id)
				)
			)
		)
	if graduate:
		query = query.where(student_models.Student.graduate == True)
	students = await db.execute(query)
	return students.scalars().all()
	


async def create_student(student: student_schemas.StudentCreate, db: AsyncSession):
	await division_handlers.get_one_division(student.group_id, db)
	if student.division_id:
		await division_handlers.get_one_division(student.division_id, db)
	query = await db.execute(
		insert(student_models.Student).
		values(**student.dict()).
		returning(student_models.Student).
		options(
			selectinload(student_models.Student.group).
			options(
				selectinload(division_models.Division.regulation),
				selectinload(division_models.Division.department_1),
				selectinload(division_models.Division.department_2),
			),
			selectinload(student_models.Student.division).
			options(
				selectinload(division_models.Division.regulation),
				selectinload(division_models.Division.department_1),
				selectinload(division_models.Division.department_2),
			)
		)
	)
	student = query.scalar_one()
	await db.commit()
	await db.refresh(student)
	return student


async def get_one_student(id: UUID, db: AsyncSession):
	query = main_query().where(student_models.Student.id==id)
	query = await db.execute(query)
	student = query.scalar()
	if student:
		return student
	raise HTTPException(
		detail=f"no student with given id: {id}",
		status_code=status.HTTP_404_NOT_FOUND
	)


async def get_student_by_name(name: str, db: AsyncSession):
	query = main_query().where(student_models.Student.name==name)
	query = await db.execute(query)
	student = query.scalar()
	if student:
		return student
	raise HTTPException(
		detail=f"no student with given name: {name}",
		status_code=status.HTTP_404_NOT_FOUND
	)


async def get_student_by_name_and_division(name: str, division: division_models.Division, db: AsyncSession):
	try:
		student = await get_student_by_name(name, db)
		if not (division.group or division.private):
			student.division = division
	except:
		if not (division.group or division.private):
			return None
		student = student_models.Student(name=name, group_id=division.id)
		db.add(student)
	await db.commit()
	await db.refresh(student)
	return student


async def update_student(id: UUID, student: student_schemas.StudentCreate, db: AsyncSession):
	await division_handlers.get_one_division(student.group_id, db)
	if student.division_id:
		await division_handlers.get_one_division(student.division_id, db)
	query = (
		update(student_models.Student).
        where(student_models.Student.id == id).
        values({**student.dict()}).
        returning(student_models.Student).
		options(
			selectinload(student_models.Student.group).
			options(
				selectinload(division_models.Division.regulation),
				selectinload(division_models.Division.department_1),
				selectinload(division_models.Division.department_2),
			),
			selectinload(student_models.Student.division).
			options(
				selectinload(division_models.Division.regulation),
				selectinload(division_models.Division.department_1),
				selectinload(division_models.Division.department_2),
			)
		)
	)
	query = await db.execute(query)
	student = query.scalar()
	if not student:
		raise HTTPException(
		detail=f"no student with given id: {id}",
		status_code=status.HTTP_404_NOT_FOUND
	)
	await db.commit()
	await db.refresh(student)
	return student


async def delete_student(id: UUID, db: AsyncSession):
	await get_one_student(id, db)
	await db.execute(
		delete(student_models.Student).
        where(student_models.Student.id == id)
	)
	await db.commit()
	return