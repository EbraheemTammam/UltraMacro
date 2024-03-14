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
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from authentication.oauth2 import get_current_user
from database import get_db, get_async_db
import schemas.user as user_schemas
from models import (
    user as user_models,
	division as division_models,
)
from handlers.user import UserHandler


user_router = APIRouter()


#	get all users
@user_router.get(
	'',
    response_model=List[user_schemas.User],
    status_code=status.HTTP_200_OK
)
async def get_users(
	handler: Annotated[UserHandler, Depends(UserHandler)]
):
    return await handler.get_all()


#	create user
@user_router.post(
	'',
    response_model=user_schemas.User,
    status_code=status.HTTP_201_CREATED
)
async def create_users(
	user: user_schemas.UserCreate,
	handler: Annotated[UserHandler, Depends(UserHandler)]
):
	return await handler.create(user)


#	get one user
@user_router.get(
	'/{id}',
    response_model=user_schemas.User,
    status_code=status.HTTP_200_OK
)
async def retreive_users(
	id: Annotated[UUID, Path(..., title='id of user to be retrieved')],
	handler: Annotated[UserHandler, Depends(UserHandler)]
):
	return await handler.get_one(id)


#	update user
@user_router.put(
	'/{id}',
    response_model=user_schemas.User,
)
async def update_users(
	id: Annotated[UUID, Path(..., title='id of user to be updated')],
	user: user_schemas.UserCreate,
	handler: Annotated[UserHandler, Depends(UserHandler)]
):
	return await handler.update(id, user)


#	delete user
@user_router.delete(
	'/{id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_users(
	id: Annotated[UUID, Path(..., title='id of user to be updated')],
	handler: Annotated[UserHandler, Depends(UserHandler)]
):
	return await handler.delete(id)