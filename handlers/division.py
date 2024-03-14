from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete
from sqlalchemy.orm import selectinload


from authentication.oauth2 import get_current_user
from database import get_async_db
from exceptions import DivisionNotFoundException

import schemas.division as division_schemas
from models import (
	regulation as regulation_models,
	department as department_models,
	division as division_models,
	user as user_models
)
from handlers.regulation import RegulationHandler
from handlers.department import DepartmentHandler



class DivisionHandler:

	def __init__(
		self,
		user: user_models.User = Depends(get_current_user), 
		db: AsyncSession = Depends(get_async_db),
		regulation_handler: RegulationHandler = Depends(RegulationHandler),
		department_handler: DepartmentHandler = Depends(DepartmentHandler)
	) -> None:
		self.user = user
		self.db = db
		self.model = division_models.Division
		self.regulation_handler = regulation_handler
		self.department_handler = department_handler
		self.NotFoundException = DivisionNotFoundException()
		self.retrieve_query = (
			select(self.model).
			options(
				selectinload(self.model.regulation),
				selectinload(self.model.department_1),
				selectinload(self.model.department_2),
			)
		)
		if not user.is_admin:
			self.retrieve_query = self.retrieve_query.where(self.model.users.any(id=user.id))


	async def get_all(self, regulation_id: int | None):
		divisions = await self.db.execute(
			self.retrieve_query
			if not regulation_id else
			self.retrieve_query.where(self.model.regulation_id==regulation_id)
		)
		return divisions.scalars().all()

	@staticmethod
	async def re_organize_input_dict(division: division_schemas.DivisionCreate):
		division = division.dict().copy()
		division['regulation_id'] = division['regulation']
		division['department_1_id'] = division['department']
		division['department_2_id'] = division['department2']
		del division['regulation']
		del division['department']
		del division['department2']
		return division


	async def create(self, division: division_schemas.DivisionCreate):
		division = await self.re_organize_input_dict(division)
		await self.regulation_handler.get_one(division['regulation_id'])
		if division['department_1_id']:
			await self.department_handler.get_one(division['department_1_id'])
		if division['department_2_id']:
			await self.department_handler.get_one(division['department_2_id'])
		query = await self.db.execute(
			insert(self.model).
			values(**division).
			returning(self.model).
			options(
				selectinload(self.model.regulation),
				selectinload(self.model.department_1),
				selectinload(self.model.department_2),
			)
		)
		division = query.scalar_one()
		await self.db.commit()
		await self.db.refresh(division)
		return division


	async def get_one(self, id: int):
		query = self.retrieve_query.where(self.model.id == id)
		query = await self.db.execute(query)
		division = query.scalar()
		if division:
			return division
		raise self.NotFoundException


	async def get_by_name(self, name: str):
		query = self.retrieve_query.where(self.model.name == name)
		query = await self.db.execute(query)
		division = query.scalar()
		if division:
			return division
		raise self.NotFoundException


	async def update(self, id: int, division: division_schemas.DivisionCreate):
		division = await self.re_organize_input_dict(division)
		await self.regulation_handler.get_one(division['regulation_id'])
		if division['department_1_id']:
			await self.department_handler.get_one(division['department_1_id'])
		if division['department_2_id']:
			await self.department_handler.get_one(division['department_2_id'])
		query = (
			update(self.model).
			where(self.model.id == id).
			values(**division).
			returning(self.model).
			options(
				selectinload(self.model.regulation),
				selectinload(self.model.department_1),
				selectinload(self.model.department_2),
			)
		)
		query = await self.db.execute(query)
		division = query.scalar()
		if not division:
			raise self.NotFoundException
		await self.db.commit()
		await self.db.refresh(division)
		return division


	async def delete(self, id: int):
		await self.get_one(id)
		await self.db.execute(
			delete(self.model).
			where(self.model.id == id)
		)
		await self.db.commit()
		return

