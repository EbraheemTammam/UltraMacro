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
from authentication.permissions import has_permission
from database import get_db, get_async_db
import schemas.regulation as regulation_schemas
import models.regulation as regulation_models
import models.user as user_models
from handlers.regulation import RegulationHandler


regulation_router = APIRouter()


#	get all regulations
@regulation_router.get(
	'',
    response_model=List[regulation_schemas.Regulation],
    status_code=status.HTTP_200_OK
)
async def get_regulations(
	handler: Annotated[RegulationHandler, Depends(RegulationHandler)]
):
    return await handler.get_all()


#	create regulation
@regulation_router.post(
	'',
    response_model=regulation_schemas.Regulation,
    status_code=status.HTTP_201_CREATED
)
async def create_regulations(
	regulation: regulation_schemas.RegulationCreate,
	handler: Annotated[RegulationHandler, Depends(RegulationHandler)]
):
	return await handler.create(regulation)


#	get one regulation
@regulation_router.get(
	'/{id}',
    response_model=regulation_schemas.Regulation,
    status_code=status.HTTP_200_OK
)
async def retreive_regulations(
	id: Annotated[int, Path(..., title='id of regulation to be retrieved')],
	handler: Annotated[RegulationHandler, Depends(RegulationHandler)]
):
	#await has_permission(user=user, class_=regulation_models.Regulation, object_id=id, db=db)
	return await handler.get_one(id)


#	update regulation
@regulation_router.put(
	'/{id}',
    response_model=regulation_schemas.Regulation,
)
async def update_regulations(
	id: Annotated[int, Path(..., title='id of regulation to be updated')],
	regulation: regulation_schemas.RegulationCreate,
	handler: Annotated[RegulationHandler, Depends(RegulationHandler)]
):
	#await has_permission(user=user, class_=regulation_models.Regulation, object_id=id, db=db)
	return await handler.update(id, regulation)


#	delete regulation
@regulation_router.delete(
	'/{id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_regulations(
	id: Annotated[int, Path(..., title='id of regulation to be updated')],
	handler: Annotated[RegulationHandler, Depends(RegulationHandler)]
):
	#await has_permission(user=user, class_=regulation_models.Regulation, object_id=id, db=db)
	return await handler.delete(id)