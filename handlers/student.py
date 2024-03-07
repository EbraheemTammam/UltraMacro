from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete
from sqlalchemy.orm import selectinload

import schemas.student as student_schemas
from models import (
	student as student_models,
	division as division_models
)
from handlers import division as division_handlers


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


async def get_all_students(db: AsyncSession, graduate: bool = False):
	query = main_query()
	if graduate:
		query = query.where(student_models.Student.graduate == True)
	query = await db.execute(query)
	return query.scalars().all()
	


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
	query = main_query().where(student_models.Student.id == id)
	query = await db.execute(query)
	student = query.scalar()
	if student:
		return student
	raise HTTPException(
		detail=f"no student with given id: {id}",
		status_code=status.HTTP_404_NOT_FOUND
	)


async def update_student(id: UUID, student: student_schemas.StudentCreate, db: AsyncSession):
	await division_handlers.get_one_division(student.group_id, db)
	if student.division_id:
		await division_handlers.get_one_division(student.division_id, db)
	query = await db.execute(
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