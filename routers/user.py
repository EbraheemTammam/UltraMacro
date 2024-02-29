from uuid import UUID
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
from database.client import get_db, get_async_db
import schemas.user as user_schemas
import models.user as user_models


user_router = APIRouter()


#	get all users
@user_router.get(
	'',
    response_model=List[user_schemas.User],
    status_code=status.HTTP_200_OK
)
async def get_users(db: Annotated[AsyncSession, Depends(get_async_db)]):
    query = await db.execute(
        select(user_models.User)
	)
    return query.scalars().all()


#	create user
@user_router.post(
	'',
    response_model=user_schemas.User,
    status_code=status.HTTP_201_CREATED
)
async def create_users(
	user: user_schemas.UserCreate,
	db: Annotated[AsyncSession, Depends(get_async_db)]
):
	query = await db.execute(
		insert(user_models.User).
		values(**user.dict()).
		returning(user_models.User)
	)
	user = query.scalar_one()
	await db.commit()
	await db.refresh(user)
	return user


#	get one user
@user_router.get(
	'/{id}',
    response_model=user_schemas.User | None,
    status_code=status.HTTP_200_OK
)
async def retreive_users(
	id: Annotated[UUID, Path(..., title='id of user to be retrieved')],
	db: Annotated[AsyncSession, Depends(get_async_db)]
):
	query = await db.execute(
		select(user_models.User).where(
			user_models.User.id == id
		)
	)
	user = query.scalar()
	if user:
		return user
	raise HTTPException(
		detail="no user with given id",
		status_code=status.HTTP_404_NOT_FOUND
	)


#	update user
@user_router.put(
	'/{id}',
    response_model=user_schemas.User,
)
async def update_users(
	id: Annotated[UUID, Path(..., title='id of user to be updated')],
	user: user_schemas.UserCreate,
	db: Annotated[AsyncSession, Depends(get_async_db)]
):
	query = await db.execute(
		update(user_models.User).
        where(user_models.User.id == id).
        values({**user.dict()}).
        returning(user_models.User)
	)
	user = query.scalar()
	if not user:
		raise HTTPException(
		detail="no user with given id",
		status_code=status.HTTP_404_NOT_FOUND
	)
	await db.commit()
	await db.refresh(user)
	return user


#	delete user
@user_router.delete(
	'/{id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_users(
	id: Annotated[UUID, Path(..., title='id of user to be updated')],
	db: Annotated[AsyncSession, Depends(get_async_db)]
):
	query = await db.execute(
		select(user_models.User).where(
			user_models.User.id == id
		)
	)
	if not query.scalar():
		raise HTTPException(
			detail="no user with given id",
			status_code=status.HTTP_404_NOT_FOUND
		)
	query = await db.execute(
		delete(user_models.User).
        where(user_models.User.id == id)
	)
	await db.commit()
	return