from fastapi import Depends
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete
from sqlalchemy.orm import selectinload

from authentication.permissions import RegulationPermission
from exceptions import RegulationNotFoundException

import schemas.regulation as regulation_schemas
from models.regulation import Regulation
from models.division import Division


class RegulationHandler:


    def __init__(self, permission_class: RegulationPermission = Depends(RegulationPermission)) -> None:
        self.permission_class = permission_class
        self.user = permission_class.user
        self.db = permission_class.db
        self.model = Regulation
        self.NotFoundException = RegulationNotFoundException()
        self.retrieve_query = select(self.model)
        if not self.user.is_admin:
            self.retrieve_query = self.retrieve_query.where(
                self.model.id.in_(
                    select(Division.regulation_id).
                    where(Division.users.any(id=self.user.id))
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
            await self.permission_class.check_permission(id)
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
        await self.permission_class.check_permission(id)
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