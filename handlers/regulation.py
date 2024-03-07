from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete
from sqlalchemy.orm import selectinload


import schemas.regulation as regulation_schemas
import models.regulation as regulation_models





async def get_all_regulations(db: AsyncSession):
    query = await db.execute(
        select(regulation_models.Regulation)
	)
    return query.scalars().all()


async def create_regulation(regulation: regulation_schemas.RegulationCreate, db: AsyncSession):
    query = await db.execute(
    	insert(regulation_models.Regulation).
    	values(**regulation.dict()).
    	returning(regulation_models.Regulation)
    )
    regulation = query.scalar_one()
    await db.commit()
    await db.refresh(regulation)
    return regulation


async def get_one_regulation(id: int, db: AsyncSession):
    query = await db.execute(
    	select(regulation_models.Regulation).where(
    		regulation_models.Regulation.id == id
    	)
    )
    regulation = query.scalar()
    if regulation:
        return regulation
    raise HTTPException(
    	detail=f"no regulation with given id: {id}",
    	status_code=status.HTTP_404_NOT_FOUND
    )


async def update_regulation(id: int, regulation: regulation_schemas.RegulationCreate, db: AsyncSession):
    query = await db.execute(
    	update(regulation_models.Regulation).
        where(regulation_models.Regulation.id == id).
        values({**regulation.dict()}).
        returning(regulation_models.Regulation)
    )
    regulation = query.scalar()
    if not regulation:
        raise HTTPException(
        detail=f"no regulation with given id: {id}",
        status_code=status.HTTP_404_NOT_FOUND
    )
    await db.commit()
    await db.refresh(regulation)
    return regulation


async def delete_regulation(id:int, db: AsyncSession):
    await get_one_regulation(id, db)
    await db.execute(
    	delete(regulation_models.Regulation).
        where(regulation_models.Regulation.id == id)
    )
    await db.commit()
    return