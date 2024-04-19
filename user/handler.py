from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.orm import selectinload

from authentication.oauth2 import TokenHandler
from generics.exceptions import UserNotFoundException, ForbiddenException


from division.models import Division

from .schemas import UserCreate
from .models import User



class UserHandler:

	def __init__(self, db: AsyncSession) -> None:
		self.db = db
		self.token_handler = TokenHandler(db)
		self.NotFoundException = UserNotFoundException()
		self.UniqueConstraintsException = ForbiddenException("user with this email already exists")
		self.retrieve_query = (
				select(User).
				options(
					selectinload(User.divisions).
					options(
						selectinload(Division.regulation),
						selectinload(Division.department_1),
						selectinload(Division.department_2),
					)
				)
			)


	async def check_email_uniqueness(self, email: str) -> bool:
		user = await self.db.execute(
			select(User.email).
			where(User.email == email)
		)
		if user.scalar():
			return False
		return True


	async def get_all(self):
		query = await self.db.execute(self.retrieve_query)
		return query.scalars().all()


	async def create(self, user: UserCreate):
		check = await self.check_email_uniqueness(user.email)
		if not check:
			raise self.UniqueConstraintsException
		new_user = User(**user.dict(exclude={'divisions'}))
		self.db.add(new_user)
		if user.divisions:
			for d in user.divisions:
				division = await self.db.get(Division, d)
				new_user.divisions.append(division)
		await self.db.commit()
		await self.db.refresh(new_user)
		await self.token_handler.create(new_user)
		return await self.get_one(new_user.id)


	async def get_one(self, id: UUID):
		query = self.retrieve_query.where(User.id == id)
		query = await self.db.execute(query)
		user = query.scalar()
		if user:
			return user
		raise self.NotFoundException


	async def update(self, id: UUID, user: UserCreate):
		check = await self.check_email_uniqueness(user.email)
		if not check:
			raise self.UniqueConstraintsException
		existing_user = await self.get_one(id)
		for key, value in user.dict(exclude={"divisions"}).items():
			setattr(existing_user, key, value)
		if user.divisions is not None:
			existing_user.divisions.clear()
			for division_id in user.divisions:
				division = await self.db.get(Division, division_id)
				if division:
					existing_user.divisions.append(division)
		await self.db.commit()
		return await self.get_one(id)


	async def delete(self, id: UUID):
		await self.db.execute(
			delete(User).
			where(User.id == id)
		)
		await self.db.commit()
		return

