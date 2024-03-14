from fastapi import HTTPException, status, Depends
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete
from sqlalchemy.orm import selectinload


from authentication.oauth2 import get_current_user
from database import get_async_db
from exceptions import DepartmentNotFoundException


import schemas.department as department_schemas
from models import (
    department as department_models,
    user as user_models,
    division as division_models
)


class DepartmentHandler:

    def __init__(self, user: user_models.User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)) -> None:
        self.user = user
        self.db = db
        self.model = department_models.Department
        self.NotFoundException = DepartmentNotFoundException()
        self.retrieve_query = select(self.model)
        if not user.is_admin:
            self.retrieve_query = self.retrieve_query.where(
                or_(
                    self.model.id.in_(
                        select(division_models.Division.department_1_id).
                        where(division_models.Division.users.any(id=user.id))
                    ),
                    self.model.id.in_(
                        select(division_models.Division.department_2_id).
                        where(division_models.Division.users.any(id=user.id))
                    )
                )
            )

    async def get_all(self):
        divisions = await self.db.execute(self.retrieve_query)
        return divisions.scalars().all()


    async def create(self, department: department_schemas.DepartmentCreate):
        query = await self.db.execute(
            insert(self.model).
            values(**department.dict()).
            returning(self.model)
        )
        department = query.scalar_one()
        await self.db.commit()
        await self.db.refresh(department)
        return department


    async def get_one(self, id: int):
        department = await self.db.get(self.model, id)
        if department:
            return department
        raise self.NotFoundException


    async def get_by_name(self, name: str):
        query = await self.db.execute(
            select(self.model).
            where(self.model.name==name)
        )
        department = query.scalar()
        if department:
            return department
        raise self.NotFoundException

    async def update(self, id: int, department: department_schemas.DepartmentCreate):
        query = (
            update(self.model).
            where(self.model.id == id).
            values({**department.dict()}).
            returning(self.model)
        )
        department = await self.db.execute(query)
        department = department.scalar()
        if not department:
            raise self.NotFoundException
        await self.db.commit()
        await self.db.refresh(department)
        return department


    async def delete(self, id: int):
        await self.get_one(id)
        await self.db.execute(
            delete(self.model).
            where(self.model.id == id)
        )
        await self.db.commit()
        return