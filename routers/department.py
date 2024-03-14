from typing import Annotated, List
from fastapi import (
	APIRouter,
	Response,
	status,
	Depends,
	Path,
	Query
)

import schemas.department as department_schemas
from handlers.department import DepartmentHandler


department_router = APIRouter()

#	get all departments
@department_router.get(
	'',
    response_model=List[department_schemas.Department],
    status_code=status.HTTP_200_OK
)
async def get_departments(
	handler: Annotated[DepartmentHandler, Depends(DepartmentHandler)]
):
    return await handler.get_all()


#	create department
@department_router.post(
	'',
    response_model=department_schemas.Department,
    status_code=status.HTTP_201_CREATED
)
async def create_departments(
	department: department_schemas.DepartmentCreate,
	handler: Annotated[DepartmentHandler, Depends(DepartmentHandler)]
):
	return await handler.create(department)


#	get one department
@department_router.get(
	'/{id}',
    response_model=department_schemas.Department,
    status_code=status.HTTP_200_OK
)
async def retrieve_departments(
	id: Annotated[int, Path(..., title='id of department to be retrieved')],
	handler: Annotated[DepartmentHandler, Depends(DepartmentHandler)]
):
	return await handler.get_one(id)


#	update department
@department_router.put(
	'/{id}',
    response_model=department_schemas.Department,
)
async def update_departments(
	id: Annotated[int, Path(..., title='id of department to be updated')],
	department: department_schemas.DepartmentCreate,
	handler: Annotated[DepartmentHandler, Depends(DepartmentHandler)]
):
	return await handler.update(id, department)


#	delete department
@department_router.delete(
	'/{id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_departments(
	id: Annotated[int, Path(..., title='id of department to be updated')],
	handler: Annotated[DepartmentHandler, Depends(DepartmentHandler)]
):
	await handler.delete(id)