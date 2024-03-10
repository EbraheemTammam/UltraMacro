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
from authentication.permissions import has_permission
from database import get_db, get_async_db
import schemas.division as division_schemas
from models import (
	division as division_models,
	regulation as regulation_models,
	department as department_models,
	user as user_models
)
import handlers.division as division_handlers


division_router = APIRouter()


#	get all divisions
@division_router.get(
	'',
    response_model=List[division_schemas.Division],
    status_code=status.HTTP_200_OK
)
async def get_divisions(
	db: Annotated[AsyncSession, Depends(get_async_db)],
	user: Annotated[user_models.User, Depends(get_current_user)]
):
    return await division_handlers.get_all_divisions(user, db)


#	create division
@division_router.post(
	'',
    response_model=division_schemas.Division,
    status_code=status.HTTP_201_CREATED
)
async def create_divisions(
	division: division_schemas.DivisionCreate,
	db: Annotated[AsyncSession, Depends(get_async_db)],
	user: Annotated[user_models.User, Depends(get_current_user)]
):
	return await division_handlers.create_division(division, db)


#	get one division
@division_router.get(
	'/{id}',
    response_model=division_schemas.Division | None,
    status_code=status.HTTP_200_OK
)
async def retreive_divisions(
	id: Annotated[int, Path(..., title='id of division to be retrieved')],
	db: Annotated[AsyncSession, Depends(get_async_db)],
	user: Annotated[user_models.User, Depends(get_current_user)]
):
	await has_permission(user=user, class_=division_models.Division, object_id=id, db=db)
	return await division_handlers.get_one_division(id, db)


#	update division
@division_router.put(
	'/{id}',
    response_model=division_schemas.Division,
)
async def update_divisions(
	id: Annotated[int, Path(..., title='id of division to be updated')],
	division: division_schemas.DivisionCreate,
	db: Annotated[AsyncSession, Depends(get_async_db)],
	user: Annotated[user_models.User, Depends(get_current_user)]
):
	await has_permission(user=user, class_=division_models.Division, object_id=id, db=db)
	return await division_handlers.update_division(id, division, db)


#	delete division
@division_router.delete(
	'/{id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_divisions(
	id: Annotated[int, Path(..., title='id of division to be updated')],
	db: Annotated[AsyncSession, Depends(get_async_db)],
	user: Annotated[user_models.User, Depends(get_current_user)]
):
	await has_permission(user=user, class_=division_models.Division, object_id=id, db=db)
	return await division_handlers.delete_division(id, db)