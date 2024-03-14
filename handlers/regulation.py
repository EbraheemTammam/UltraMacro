from fastapi import HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete
from sqlalchemy.orm import selectinload

from authentication.oauth2 import get_current_user
from database import get_async_db
from exceptions import RegulationNotFoundException

import schemas.regulation as regulation_schemas
from models import (
    regulation as regulation_models,
    user as user_models,
    division as division_models
)


class RegulationHandler:


    def __init__(self, user: user_models.User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)) -> None:
        self.user = user
        self.db = db
        self.model = regulation_models.Regulation
        self.NotFoundException = RegulationNotFoundException()
        self.retrieve_query = select(self.model)
        if not user.is_admin:
            self.retrieve_query = self.retrieve_query.where(
                self.model.id.in_(
                    select(division_models.Division.regulation_id).
                    where(division_models.Division.users.any(id=user.id))
                )
            )

    async def get_all(self):
        regulations = await self.db.execute(self.retrieve_query)
        return regulations.scalars().all()


    async def create(self, regulation: regulation_schemas.RegulationCreate):
        query = await self.db.execute(
            insert(self.model).
            values(**regulation.dict()).
            returning(self.model)
        )
        regulation = query.scalar_one()
        await self.db.commit()
        await self.db.refresh(regulation)
        return regulation


    async def get_one(self, id: int):
        regulation = await self.db.get(self.model, id)
        if regulation:
            return regulation
        raise self.NotFoundException


    async def update(self, id: int, regulation: regulation_schemas.RegulationCreate):
        query = (
            update(self.model).
            where(self.model.id == id).
            values({**regulation.dict()}).
            returning(self.model)
        )
        result = await self.db.execute(query)
        regulation = result.scalar()
        if not regulation:
            raise self.NotFoundException
        await self.db.commit()
        await self.db.refresh(regulation)
        return regulation


    async def delete(self, id: int):
        await self.get_one(id)
        await self.db.execute(
            delete(self.model).
            where(self.model.id == id)
        )
        await self.db.commit()
        return