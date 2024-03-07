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
from database import get_db, get_async_db
import schemas.department as department_schemas
import models.department as department_models
import models.user as user_models
import handlers.department as department_handlers


department_router = APIRouter()

#	get all departments
@department_router.get(
	'',
    response_model=List[department_schemas.Department],
    status_code=status.HTTP_200_OK
)
async def get_departments(
	db: Annotated[AsyncSession, Depends(get_async_db)],
	user: Annotated[user_models.User, Depends(get_current_user)]
):
    return await department_handlers.get_all_departments(db)


#	create department
@department_router.post(
	'',
    response_model=department_schemas.Department,
    status_code=status.HTTP_201_CREATED
)
async def create_departments(
	department: department_schemas.DepartmentCreate,
	db: Annotated[AsyncSession, Depends(get_async_db)],
	user: Annotated[user_models.User, Depends(get_current_user)]
):
	return await department_handlers.create_department(department, db)


#	get one department
@department_router.get(
	'/{id}',
    response_model=department_schemas.Department | None,
    status_code=status.HTTP_200_OK
)
async def retreive_departments(
	id: Annotated[int, Path(..., title='id of department to be retrieved')],
	db: Annotated[AsyncSession, Depends(get_async_db)],
	user: Annotated[user_models.User, Depends(get_current_user)]
):
	return await department_handlers.get_one_department(id, db)


#	update department
@department_router.put(
	'/{id}',
    response_model=department_schemas.Department,
)
async def update_departments(
	id: Annotated[int, Path(..., title='id of department to be updated')],
	department: department_schemas.DepartmentCreate,
	db: Annotated[AsyncSession, Depends(get_async_db)],
	user: Annotated[user_models.User, Depends(get_current_user)]
):
	return await department_handlers.update_department(id, department, db)


#	delete department
@department_router.delete(
	'/{id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_departments(
	id: Annotated[int, Path(..., title='id of department to be updated')],
	db: Annotated[AsyncSession, Depends(get_async_db)],
	user: Annotated[user_models.User, Depends(get_current_user)]
):
	await department_handlers.delete_department(id, db)