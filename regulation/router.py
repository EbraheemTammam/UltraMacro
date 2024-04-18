from typing import Annotated, List
from fastapi import (
	APIRouter,
	Response,
	status,
	Depends,
	Path,
	Query
)

from generics.permissions import RegulationPermission

from .schemas import RegulationCreate, Regulation
from .handler import RegulationHandler


regulation_router = APIRouter()


#	get all regulations
@regulation_router.get(
	'',
    response_model=List[Regulation],
    status_code=status.HTTP_200_OK
)
async def get_regulations(
	permission_class: Annotated[RegulationPermission, Depends(RegulationPermission)]
):
	handler = RegulationHandler(permission_class.user, permission_class.db)
	return await handler.get_all()


#	create regulation
@regulation_router.post(
	'',
    response_model=Regulation,
    status_code=status.HTTP_201_CREATED
)
async def create_regulations(
	regulation: RegulationCreate,
	permission_class: Annotated[RegulationPermission, Depends(RegulationPermission)]
):
	handler = RegulationHandler(permission_class.user, permission_class.db)
	return await handler.create(regulation)


#	get one regulation
@regulation_router.get(
	'/{id}',
    response_model=Regulation,
    status_code=status.HTTP_200_OK
)
async def retrieve_regulations(
	id: Annotated[int, Path(..., title='id of regulation to be retrieved')],
	permission_class: Annotated[RegulationPermission, Depends(RegulationPermission)]
):
	await permission_class.check_permission(id)
	handler = RegulationHandler(permission_class.user, permission_class.db)
	return await handler.get_one(id)


#	update regulation
@regulation_router.put(
	'/{id}',
    response_model=Regulation,
)
async def update_regulations(
	id: Annotated[int, Path(..., title='id of regulation to be updated')],
	regulation: RegulationCreate,
	permission_class: Annotated[RegulationPermission, Depends(RegulationPermission)]
):
	await permission_class.check_permission(id)
	handler = RegulationHandler(permission_class.user, permission_class.db)
	return await handler.update(id, regulation)


#	delete regulation
@regulation_router.delete(
	'/{id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_regulations(
	id: Annotated[int, Path(..., title='id of regulation to be updated')],
	permission_class: Annotated[RegulationPermission, Depends(RegulationPermission)]
):
	await permission_class.check_permission(id)
	handler = RegulationHandler(permission_class.user, permission_class.db)
	await handler.get_one(id)
	return await handler.delete(id)