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
from sqlalchemy import insert, update, delete
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from authentication.oauth2 import get_current_user
from database import get_db, get_async_db
import schemas.regulation as regulation_schemas
import models.regulation as regulation_models
import models.user as user_models


regulation_router = APIRouter()


#	get all regulations
@regulation_router.get(
	'',
    response_model=List[regulation_schemas.Regulation],
    status_code=status.HTTP_200_OK
)
async def get_regulations(
	db: Annotated[AsyncSession, Depends(get_async_db)],
	user: Annotated[user_models.User, Depends(get_current_user)]
):
    query = await db.execute(
        select(regulation_models.Regulation)
	)
    return query.scalars().all()


#	create regulation
@regulation_router.post(
	'',
    response_model=regulation_schemas.Regulation,
    status_code=status.HTTP_201_CREATED
)
async def create_regulations(
	regulation: regulation_schemas.RegulationCreate,
	db: Annotated[AsyncSession, Depends(get_async_db)],
	user: Annotated[user_models.User, Depends(get_current_user)]
):
	query = await db.execute(
		insert(regulation_models.Regulation).
		values(**regulation.dict()).
		returning(regulation_models.Regulation)
	)
	regulation = query.scalar_one()
	await db.commit()
	await db.refresh(regulation)
	return regulation


#	get one regulation
@regulation_router.get(
	'/{id}',
    response_model=regulation_schemas.Regulation | None,
    status_code=status.HTTP_200_OK
)
async def retreive_regulations(
	id: Annotated[int, Path(..., title='id of regulation to be retrieved')],
	db: Annotated[AsyncSession, Depends(get_async_db)],
	user: Annotated[user_models.User, Depends(get_current_user)]
):
	query = await db.execute(
		select(regulation_models.Regulation).where(
			regulation_models.Regulation.id == id
		)
	)
	regulation = query.scalar()
	if regulation:
		return regulation
	raise HTTPException(
		detail="no regulation with given id",
		status_code=status.HTTP_404_NOT_FOUND
	)


#	update regulation
@regulation_router.put(
	'/{id}',
    response_model=regulation_schemas.Regulation,
)
async def update_regulations(
	id: Annotated[int, Path(..., title='id of regulation to be updated')],
	regulation: regulation_schemas.RegulationCreate,
	db: Annotated[AsyncSession, Depends(get_async_db)],
	user: Annotated[user_models.User, Depends(get_current_user)]
):
	query = await db.execute(
		update(regulation_models.Regulation).
        where(regulation_models.Regulation.id == id).
        values({**regulation.dict()}).
        returning(regulation_models.Regulation)
	)
	regulation = query.scalar()
	if not regulation:
		raise HTTPException(
		detail="no regulation with given id",
		status_code=status.HTTP_404_NOT_FOUND
	)
	await db.commit()
	await db.refresh(regulation)
	return regulation


#	delete regulation
@regulation_router.delete(
	'/{id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_regulations(
	id: Annotated[int, Path(..., title='id of regulation to be updated')],
	db: Annotated[AsyncSession, Depends(get_async_db)],
	user: Annotated[user_models.User, Depends(get_current_user)]
):
	query = await db.execute(
		select(regulation_models.Regulation).where(
			regulation_models.Regulation.id == id
		)
	)
	if not query.scalar():
		raise HTTPException(
			detail="no regulation with given id",
			status_code=status.HTTP_404_NOT_FOUND
		)
	query = await db.execute(
		delete(regulation_models.Regulation).
        where(regulation_models.Regulation.id == id)
	)
	await db.commit()
	return