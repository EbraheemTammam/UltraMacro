from uuid import UUID
from typing import Annotated, List

from fastapi import (
	APIRouter,
	status,
	Depends,
	Path,
	Query
)

from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_db

from generics.permissions import AdminPermission

from .schemas import UserCreate, User
from .handler import UserHandler


user_router = APIRouter()


#	get all users
@user_router.get(
	'',
    response_model=List[User],
    status_code=status.HTTP_200_OK
)
async def get_users(
	permission_class: Annotated[AdminPermission, Depends(AdminPermission)],
	db: Annotated[AsyncSession, Depends(get_async_db)]
):
	handler = UserHandler(db)
	return await handler.get_all()


#	create user
@user_router.post(
	'',
    response_model=User,
    status_code=status.HTTP_201_CREATED
)
async def create_users(
	user: UserCreate,
	permission_class: Annotated[AdminPermission, Depends(AdminPermission)],
	db: Annotated[AsyncSession, Depends(get_async_db)]
):
	handler = UserHandler(db)
	return await handler.create(user)


#	get one user
@user_router.get(
	'/{id}',
    response_model=User,
    status_code=status.HTTP_200_OK
)
async def retrieve_users(
	id: Annotated[UUID, Path(..., title='id of user to be retrieved')],
	permission_class: Annotated[AdminPermission, Depends(AdminPermission)],
	db: Annotated[AsyncSession, Depends(get_async_db)]
):
	handler = UserHandler(db)
	return await handler.get_one(id)


#	update user
@user_router.put(
	'/{id}',
    response_model=User,
)
async def update_users(
	id: Annotated[UUID, Path(..., title='id of user to be updated')],
	user: UserCreate,
	permission_class: Annotated[AdminPermission, Depends(AdminPermission)],
	db: Annotated[AsyncSession, Depends(get_async_db)]
):
	handler = UserHandler(db)
	return await handler.update(id, user)


#	delete user
@user_router.delete(
	'/{id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_users(
	id: Annotated[UUID, Path(..., title='id of user to be updated')],
	permission_class: Annotated[AdminPermission, Depends(AdminPermission)],
	db: Annotated[AsyncSession, Depends(get_async_db)]
):
	handler = UserHandler(db)
	await handler.get_one(id)
	return await handler.delete(id)