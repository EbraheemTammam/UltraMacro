from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete


from generics.exceptions import RegulationNotFoundException

from .schemas import RegulationCreate
from .models import Regulation

from user.models import User
from division.models import Division


class RegulationHandler:


    def __init__(self, user: User, db: AsyncSession) -> None:
        self.user = user
        self.db = db
        self.NotFoundException = RegulationNotFoundException()
        self.retrieve_query = select(Regulation)
        if not self.user.is_admin:
            self.retrieve_query = self.retrieve_query.where(
                Regulation.id.in_(
                    select(Division.regulation_id).
                    where(Division.users.any(id=self.user.id))
                )
            )

    async def get_all(self):
        regulations = await self.db.execute(self.retrieve_query)
        return regulations.scalars().all()


    async def create(self, regulation: RegulationCreate):
        query = await self.db.execute(
            insert(Regulation).
            values(**regulation.dict()).
            returning(Regulation)
        )
        regulation = query.scalar_one()
        await self.db.commit()
        await self.db.refresh(regulation)
        return regulation


    async def get_one(self, id: int):
        regulation = await self.db.get(Regulation, id)
        if regulation:
            return regulation
        raise self.NotFoundException
    

    async def get_by_name(self, name: str):
        regulation = await self.db.execute(
            select(Regulation).where(Regulation.name==name)
        )
        return regulation.scalar()


    async def update(self, id: int, regulation: RegulationCreate):
        query = (
            update(Regulation).
            where(Regulation.id == id).
            values({**regulation.dict()}).
            returning(Regulation)
        )
        result = await self.db.execute(query)
        regulation = result.scalar()
        if not regulation:
            raise self.NotFoundException
        await self.db.commit()
        await self.db.refresh(regulation)
        return regulation


    async def delete(self, id: int):
        await self.db.execute(
            delete(Regulation).
            where(Regulation.id == id)
        )
        await self.db.commit()
        return