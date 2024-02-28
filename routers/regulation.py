from typing import Annotated, List
from fastapi import (
	APIRouter,
	Response,
	status,
	HTTPException,
	Depends,
	Path,
	Query
)
from sqlalchemy import insert
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from authentication.oauth2 import get_current_user
from database.client import get_db, get_async_db
import schemas.regulation as regulation_schemas
import models.regulation as regulation_models


regulation_router = APIRouter()


@regulation_router.get(
	'',
    response_model=List[regulation_schemas.Regulation],
    status_code=status.HTTP_200_OK
)
async def get_regulations(db: Annotated[AsyncSession, Depends(get_async_db)]):
    query = await db.execute(
        select(regulation_models.Regulation)
	)
    return query.scalars().all()


@regulation_router.post(
	'',
    response_model=regulation_schemas.Regulation,
    status_code=status.HTTP_201_CREATED
)
async def get_regulations(
	regulation: regulation_schemas.RegulationCreate,
	db: Annotated[AsyncSession, Depends(get_async_db)]
):
	query = await db.execute(
		insert(regulation_models.Regulation).returning(regulation_models.Regulation),
		[regulation]
	)
	await db.commit()
	return query.scalar_one()


@regulation_router.get(
	'/{id}',
    response_model=regulation_schemas.Regulation | None,
    status_code=status.HTTP_200_OK
)
async def get_regulations(
	id: Annotated[int, Path(..., title='id of regulation to be retrieved')],
	db: Annotated[AsyncSession, Depends(get_async_db)]
):
	query = await db.execute(
		select(regulation_models.Regulation).where(
			regulation_models.Regulation.id == id
		)
	)
	if query:
		return query.scalar_one_or_none()
	raise HTTPException(
		detail="no regulation with given id",
		status_code=status.HTTP_404_NOT_FOUND
	)