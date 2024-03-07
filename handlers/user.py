from typing import Any
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete
from sqlalchemy.orm import selectinload

import schemas.user as user_schemas
from models import (
    user as user_models,
	regulation as regulation_models,
	department as department_models,
    division as division_models,
	course as course_models,
	student as student_models
)


def main_query():
	return (
		select(user_models.User).
		options(
			selectinload(user_models.User.divisions).
			options(
				selectinload(division_models.Division.regulation),
				selectinload(division_models.Division.department_1),
				selectinload(division_models.Division.department_2),
			)
		)
	)


async def check_email_uniqueness(email: str, db: AsyncSession):
	user = await db.execute(
		select(user_models.User).
		where(user_models.User.email == email)
	)
	if user.scalar():
		raise HTTPException(
			detail="Email already exists",
			status_code=status.HTTP_403_FORBIDDEN
		)
	return


async def get_all_users(db: AsyncSession):
	query = await db.execute(main_query())
	return query.scalars().all()


async def create_user(user: user_schemas.UserCreate, db: AsyncSession):
	await check_email_uniqueness(user.email, db)
	query = await db.execute(
		insert(user_models.User).
		values({
			'email': user.email,
			'first_name': user.first_name,
			'last_name': user.last_name,
			'password': user.password,
			'is_admin': user.is_admin,
		}).
		returning(user_models.User).
		options(
			selectinload(user_models.User.divisions).
			options(
				selectinload(division_models.Division.regulation),
				selectinload(division_models.Division.department_1),
				selectinload(division_models.Division.department_2),
			)
		)
	)
	user = query.scalar_one()
	await db.commit()
	await db.refresh(user)
	return user


async def get_one_user(id: UUID, db: AsyncSession):
	query = main_query().where(user_models.User.id == id)
	query = await db.execute(query)
	user = query.scalar()
	if user:
		return user
	raise HTTPException(
		detail=f"no user with given id: {id}",
		status_code=status.HTTP_404_NOT_FOUND
	)


async def update_user(id: UUID, user: user_schemas.UserCreate, db: AsyncSession):
	await check_email_uniqueness(user.email, db)
	query = await db.execute(
		update(user_models.User).
        where(user_models.User.id == id).
        values({
			'email': user.email,
			'first_name': user.first_name,
			'last_name': user.last_name,
			'password': user.password,
			'is_admin': user.is_admin,
		}).
        returning(user_models.User).
		options(
			selectinload(user_models.User.divisions).
			options(
				selectinload(division_models.Division.regulation),
				selectinload(division_models.Division.department_1),
				selectinload(division_models.Division.department_2),
			)
		)
	)
	user = query.scalar()
	if not user:
		raise HTTPException(
		detail=f"no user with given id: {id}",
		status_code=status.HTTP_404_NOT_FOUND
	)
	await db.commit()
	await db.refresh(user)
	return user


async def delete_user(id: UUID, db: AsyncSession):
	await get_one_user(id, db)
	await db.execute(
		delete(user_models.User).
        where(user_models.User.id == id)
	)
	await db.commit()
	return

