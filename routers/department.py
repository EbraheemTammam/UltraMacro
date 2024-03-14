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
import schemas.department as department_schemas
import models.department as department_models
import models.user as user_models
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
async def retreive_departments(
	id: Annotated[int, Path(..., title='id of department to be retrieved')],
	handler: Annotated[DepartmentHandler, Depends(DepartmentHandler)]
):
	#await has_permission(user=user, class_=department_models.Department, object_id=id, db=db)
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
	#await has_permission(user=user, class_=department_models.Department, object_id=id, db=db)
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
	#await has_permission(user=user, class_=department_models.Department, object_id=id, db=db)
	await handler.delete(id)