from typing import Any
from uuid import UUID
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete
from sqlalchemy.orm import selectinload

from authentication.permissions import AdminPermission
from authentication.oauth2 import TokenHandler
from database import get_async_db
from exceptions import UserNotFoundException, ForbiddenException


import schemas.user as user_schemas
from models import (
    user as user_models,
    division as division_models,
)



class UserHandler:

	def __init__(
		self, 
		permission_class: AdminPermission = Depends(AdminPermission), 
		token_handler: TokenHandler = Depends(TokenHandler)
	) -> None:
		self.user = permission_class.user
		self.db = token_handler.db
		self.token_handler = token_handler
		self.model = user_models.User
		self.NotFoundException = UserNotFoundException()
		self.UniqueConstraintsException = ForbiddenException("user with this email already exists")
		self.retrieve_query = (
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


	async def check_email_uniqueness(self, email: str) -> bool:
		user = await self.db.execute(
			select(user_models.User.email).
			where(user_models.User.email == email)
		)
		if user.scalar():
			return False
		return True


	async def get_all(self):
		query = await self.db.execute(self.retrieve_query)
		return query.scalars().all()


	async def create(self, user: user_schemas.UserCreate):
		check = await self.check_email_uniqueness(user.email)
		if not check:
			raise self.UniqueConstraintsException
		new_user = user_models.User(**user.dict(exclude={'divisions'}))
		self.db.add(new_user)
		if user.divisions:
			for d in user.divisions:
				division = await self.db.get(division_models.Division, d)
				new_user.divisions.append(division)
		await self.db.commit()
		await self.db.refresh(new_user)
		await self.token_handler.create(new_user)
		return await self.get_one(new_user.id)


	async def get_one(self, id: UUID):
		query = self.retrieve_query.where(user_models.User.id == id)
		query = await self.db.execute(query)
		user = query.scalar()
		if user:
			return user
		raise self.NotFoundException


	async def update(self, id: UUID, user: user_schemas.UserCreate):
		check = await self.check_email_uniqueness(user.email)
		if not check:
			raise self.UniqueConstraintsException
		existing_user = await self.get_one(id)
		for key, value in user.dict(exclude={"divisions"}).items():
			setattr(existing_user, key, value)
		if user.divisions is not None:
			existing_user.divisions.clear()
			for division_id in user.divisions:
				division = await self.db.get(division_models.Division, division_id)
				if division:
					existing_user.divisions.append(division)
		await self.db.commit()
		await self.db.refresh(existing_user)
		return existing_user


	async def delete(self, id: UUID):
		await self.get_one(id)
		await self.db.execute(
			delete(user_models.User).
			where(user_models.User.id == id)
		)
		await self.db.commit()
		return

