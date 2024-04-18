from typing import Annotated, List
from fastapi import (
	APIRouter,
	Response,
	status,
	Depends,
	Path,
	Query
)

from generics.permissions import DepartmentPermission

from .schemas import DepartmentCreate, Department
from .handler import DepartmentHandler


department_router = APIRouter()

#	get all departments
@department_router.get(
	'',
    response_model=List[Department],
    status_code=status.HTTP_200_OK
)
async def get_departments(
	permission_class: Annotated[DepartmentPermission, Depends(DepartmentPermission)]
):
	handler = DepartmentHandler(permission_class.user, permission_class.db)
	return await handler.get_all()


#	create department
@department_router.post(
	'',
    response_model=Department,
    status_code=status.HTTP_201_CREATED
)
async def create_departments(
	department: DepartmentCreate,
	permission_class: Annotated[DepartmentPermission, Depends(DepartmentPermission)]
):
	handler = DepartmentHandler(permission_class.user, permission_class.db)
	return await handler.create(department)


#	get one department
@department_router.get(
	'/{id}',
    response_model=Department,
    status_code=status.HTTP_200_OK
)
async def retrieve_departments(
	id: Annotated[int, Path(..., title='id of department to be retrieved')],
	permission_class: Annotated[DepartmentPermission, Depends(DepartmentPermission)]
):
	await permission_class.check_permission(id)
	handler = DepartmentHandler(permission_class.user, permission_class.db)
	return await handler.get_one(id)


#	update department
@department_router.put(
	'/{id}',
    response_model=Department,
)
async def update_departments(
	id: Annotated[int, Path(..., title='id of department to be updated')],
	department: DepartmentCreate,
	permission_class: Annotated[DepartmentPermission, Depends(DepartmentPermission)]
):
	await permission_class.check_permission(id)
	handler = DepartmentHandler(permission_class.user, permission_class.db)
	return await handler.update(id, department)


#	delete department
@department_router.delete(
	'/{id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_departments(
	id: Annotated[int, Path(..., title='id of department to be updated')],
	permission_class: Annotated[DepartmentPermission, Depends(DepartmentPermission)]
):
	await permission_class.check_permission(id)
	handler = DepartmentHandler(permission_class.user, permission_class.db)
	await handler.get_one(id)
	return await handler.delete(id)