from fastapi import Depends
from sqlalchemy import or_
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete
from sqlalchemy.orm import selectinload


from exceptions import DepartmentNotFoundException
from authentication.permissions import DepartmentPermission


import schemas.department as department_schemas
from models.department import Department
from models.division import Division


class DepartmentHandler:

    def __init__(self, permission_class: DepartmentPermission = Depends(DepartmentPermission)) -> None:
        self.user = permission_class.user
        self.db = permission_class.db
        self.permission_class = permission_class
        self.model = Department
        self.NotFoundException = DepartmentNotFoundException()
        self.retrieve_query = select(self.model)
        if not self.user.is_admin:
            self.retrieve_query = self.retrieve_query.where(
                or_(
                    self.model.id.in_(
                        select(Division.department_1_id).
                        where(Division.users.any(id=self.user.id))
                    ),
                    self.model.id.in_(
                        select(Division.department_2_id).
                        where(Division.users.any(id=self.user.id))
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
            await self.permission_class.check_permission(id)
            return department
        raise self.NotFoundException


    async def get_by_name(self, name: str):
        query = await self.db.execute(
            select(self.model).
            where(self.model.name==name)
        )
        department = query.scalar()
        if department:
            await self.permission_class.check_permission(department.id)
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
        await self.permission_class.check_permission(id)
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