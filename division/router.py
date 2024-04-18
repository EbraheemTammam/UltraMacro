from typing import Annotated, List
from fastapi import (
	APIRouter,
	status,
	Depends,
	Path,
	Query
)

from generics.permissions import DivisionPermission

from .schemas import DivisionCreate, Division
from .handler import DivisionHandler


division_router = APIRouter()


#	get all divisions
@division_router.get(
	'',
    response_model=List[Division],
    status_code=status.HTTP_200_OK
)
async def get_divisions(
	permission_class: Annotated[DivisionPermission, Depends(DivisionPermission)],
	regulation: int = Query(None, title='id of regulation to filter result')
):
	handler = DivisionHandler(permission_class.user, permission_class.db)
	return await handler.get_all(regulation)


#	create division
@division_router.post(
	'',
    response_model=Division,
    status_code=status.HTTP_201_CREATED
)
async def create_divisions(
	division: DivisionCreate,
	permission_class: Annotated[DivisionPermission, Depends(DivisionPermission)]
):
	handler = DivisionHandler(permission_class.user, permission_class.db)
	return await handler.create(division)


#	get one division
@division_router.get(
	'/{id}',
    response_model=Division,
    status_code=status.HTTP_200_OK
)
async def retrieve_divisions(
	id: Annotated[int, Path(..., title='id of division to be retrieved')],
	permission_class: Annotated[DivisionPermission, Depends(DivisionPermission)]
):
	await permission_class.check_permission(id)
	handler = DivisionHandler(permission_class.user, permission_class.db)
	return await handler.get_one(id)


#	update division
@division_router.put(
	'/{id}',
    response_model=Division,
)
async def update_divisions(
	id: Annotated[int, Path(..., title='id of division to be updated')],
	division: DivisionCreate,
	permission_class: Annotated[DivisionPermission, Depends(DivisionPermission)]
):
	await permission_class.check_permission(id)
	handler = DivisionHandler(permission_class.user, permission_class.db)
	return await handler.update(id, division)


#	delete division
@division_router.delete(
	'/{id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_divisions(
	id: Annotated[int, Path(..., title='id of division to be updated')],
	permission_class: Annotated[DivisionPermission, Depends(DivisionPermission)]
):
	await permission_class.check_permission(id)
	handler = DivisionHandler(permission_class.user, permission_class.db)
	await handler.get_one(id)
	return await handler.delete(id)