from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete
from sqlalchemy.orm import selectinload

from generics.exceptions import DivisionNotFoundException

from .schemas import DivisionCreate
from .models import Division

from regulation.handler import RegulationHandler
from department.handler import DepartmentHandler
from user.models import User



class DivisionHandler:

	def __init__(self, user: User, db: AsyncSession) -> None:
		self.user = user
		self.db = db
		self.regulation_handler = RegulationHandler(user, db)
		self.department_handler = DepartmentHandler(user, db)
		self.NotFoundException = DivisionNotFoundException()
		self.retrieve_query = (
			select(Division).
			options(
				selectinload(Division.regulation),
				selectinload(Division.department_1),
				selectinload(Division.department_2),
			)
		)
		if not self.user.is_admin:
			self.retrieve_query = self.retrieve_query.where(Division.users.any(id=self.user.id))


	async def get_all(self, regulation_id: int | None):
		divisions = await self.db.execute(
			self.retrieve_query
			if not regulation_id else
			self.retrieve_query.where(Division.regulation_id==regulation_id)
		)
		return divisions.scalars().all()

	@staticmethod
	async def re_organize_input_dict(division: DivisionCreate):
		division = division.dict().copy()
		division['regulation_id'] = division['regulation']
		division['department_1_id'] = division['department']
		division['department_2_id'] = division['department2']
		del division['regulation']
		del division['department']
		del division['department2']
		return division


	async def create(self, division: DivisionCreate):
		division = await self.re_organize_input_dict(division)
		await self.regulation_handler.get_one(division['regulation_id'])
		if division['department_1_id']:
			await self.department_handler.get_one(division['department_1_id'])
		if division['department_2_id']:
			await self.department_handler.get_one(division['department_2_id'])
		query = await self.db.execute(
			insert(Division).
			values(**division).
			returning(Division).
			options(
				selectinload(Division.regulation),
				selectinload(Division.department_1),
				selectinload(Division.department_2),
			)
		)
		division = query.scalar_one()
		await self.db.commit()
		await self.db.refresh(division)
		return division


	async def get_one(self, id: int):
		query = self.retrieve_query.where(Division.id == id)
		query = await self.db.execute(query)
		division = query.scalar()
		if division:
			return division
		raise self.NotFoundException


	async def get_by_name(self, name: str):
		query = self.retrieve_query.where(Division.name == name)
		query = await self.db.execute(query)
		division = query.scalar()
		if division:
			return division
		raise self.NotFoundException


	async def update(self, id: int, division: DivisionCreate):
		division = await self.re_organize_input_dict(division)
		await self.regulation_handler.get_one(division['regulation_id'])
		if division['department_1_id']:
			await self.department_handler.get_one(division['department_1_id'])
		if division['department_2_id']:
			await self.department_handler.get_one(division['department_2_id'])
		query = (
			update(Division).
			where(Division.id == id).
			values(**division).
			returning(Division).
			options(
				selectinload(Division.regulation),
				selectinload(Division.department_1),
				selectinload(Division.department_2),
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
		await self.db.execute(
			delete(Division).
			where(Division.id == id)
		)
		await self.db.commit()
		return

