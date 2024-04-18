from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete


from generics.exceptions import DepartmentNotFoundException


from .schemas import DepartmentCreate
from .models import Department

from division.models import Division
from user.models import User


class DepartmentHandler:

    def __init__(self, user: User, db: AsyncSession) -> None:
        self.user = user
        self.db = db
        self.NotFoundException = DepartmentNotFoundException()
        self.retrieve_query = select(Department)
        if not self.user.is_admin:
            self.retrieve_query = self.retrieve_query.where(
                or_(
                    Department.id.in_(
                        select(Division.department_1_id).
                        where(Division.users.any(id=self.user.id))
                    ),
                    Department.id.in_(
                        select(Division.department_2_id).
                        where(Division.users.any(id=self.user.id))
                    )
                )
            )

    async def get_all(self):
        divisions = await self.db.execute(self.retrieve_query)
        return divisions.scalars().all()


    async def create(self, department: DepartmentCreate):
        query = await self.db.execute(
            insert(Department).
            values(**department.dict()).
            returning(Department)
        )
        department = query.scalar_one()
        await self.db.commit()
        await self.db.refresh(department)
        return department


    async def get_one(self, id: int):
        department = await self.db.get(Department, id)
        if department:
            return department
        raise self.NotFoundException


    async def get_by_name(self, name: str):
        query = await self.db.execute(
            select(Department).
            where(Department.name==name)
        )
        department = query.scalar()
        if department:
            return department
        raise self.NotFoundException

    async def update(self, id: int, department: DepartmentCreate):
        query = (
            update(Department).
            where(Department.id == id).
            values({**department.dict()}).
            returning(Department)
        )
        department = await self.db.execute(query)
        department = department.scalar()
        if not department:
            raise self.NotFoundException
        await self.db.commit()
        await self.db.refresh(department)
        return department


    async def delete(self, id: int):
        await self.db.execute(
            delete(Department).
            where(Department.id == id)
        )
        await self.db.commit()
        return