from typing import Annotated, List
from fastapi import (
	APIRouter,
	Response,
	status,
	Depends,
	Path,
	Query
)

import schemas.regulation as regulation_schemas
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
async def retrieve_regulations(
	id: Annotated[int, Path(..., title='id of regulation to be retrieved')],
	handler: Annotated[RegulationHandler, Depends(RegulationHandler)]
):
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
	return await handler.delete(id)