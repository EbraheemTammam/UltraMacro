from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete
from sqlalchemy.orm import selectinload

import schemas.division as division_schemas
from models import (
	regulation as regulation_models,
	department as department_models,
	division as division_models,
	user as user_models
)
from handlers import (
	regulation as regulation_handlers,
	department as department_handlers
)



def main_query():
	return (
	    select(division_models.Division).
		options(
			selectinload(division_models.Division.regulation),
			selectinload(division_models.Division.department_1),
			selectinload(division_models.Division.department_2),
		)
	)


async def get_all_divisions(regulation_id: int | None, user: user_models.User, db: AsyncSession):
	query = main_query()
	if not user.is_admin:
		query = query.where(division_models.Division.users.any(id=user.id))
	if regulation_id:
		query = query.where(division_models.Division.regulation_id==regulation_id)
	divisions = await db.execute(query)
	return divisions.scalars().all()


async def create_division(division: division_schemas.DivisionCreate, db: AsyncSession):
	division = division.dict().copy()
	division['regulation_id'] = division['regulation']
	division['department_1_id'] = division['department']
	division['department_2_id'] = division['department2']
	del division['regulation']
	del division['department']
	del division['department2']
	await regulation_handlers.get_one_regulation(division['regulation_id'], db)
	if division['department_1_id']:
		await department_handlers.get_one_department(division['department_1_id'], db)
	if division['department_2_id']:
		await department_handlers.get_one_department(division['department_2_id'], db)
	query = await db.execute(
		insert(division_models.Division).
		values(**division).
		returning(division_models.Division).
		options(
			selectinload(division_models.Division.regulation),
			selectinload(division_models.Division.department_1),
			selectinload(division_models.Division.department_2),
		)
	)
	division = query.scalar_one()
	await db.commit()
	await db.refresh(division)
	return division


async def get_one_division(id: int, db: AsyncSession):
	query = main_query().where(division_models.Division.id == id)
	query = await db.execute(query)
	division = query.scalar()
	if division:
		return division
	raise HTTPException(
		detail=f"no division with given id: {id}",
		status_code=status.HTTP_404_NOT_FOUND
	)


async def get_division_by_name(name: str, db: AsyncSession):
	query = main_query().where(division_models.Division.name == name)
	query = await db.execute(query)
	division = query.scalar()
	if division:
		return division
	raise HTTPException(
		detail=f"no division with given name: {name}",
		status_code=status.HTTP_404_NOT_FOUND
	)


async def update_division(id: int, division: division_schemas.DivisionCreate, db: AsyncSession):
	division = division.dict().copy()
	division['regulation_id'] = division['regulation']
	division['department_1_id'] = division['department']
	division['department_2_id'] = division['department2']
	del division['regulation']
	del division['department']
	del division['department2']
	await regulation_handlers.get_one_regulation(division['regulation_id'], db)
	if division['department_1_id']:
		await department_handlers.get_one_department(division['department_1_id'], db)
	if division['department_2_id']:
		await department_handlers.get_one_department(division['department_2_id'], db)
	query = (
		update(division_models.Division).
        where(division_models.Division.id == id).
        values(**division).
        returning(division_models.Division).
		options(
			selectinload(division_models.Division.regulation),
			selectinload(division_models.Division.department_1),
			selectinload(division_models.Division.department_2),
		)
	)
	query = await db.execute(query)
	division = query.scalar()
	if not division:
		raise HTTPException(
		detail=f"no division with given id: {id}",
		status_code=status.HTTP_404_NOT_FOUND
	)
	await db.commit()
	await db.refresh(division)
	return division


async def delete_division(id:int, db: AsyncSession):
	await get_one_division(id, db)
	await db.execute(
		delete(division_models.Division).
        where(division_models.Division.id == id)
	)
	await db.commit()
	return

