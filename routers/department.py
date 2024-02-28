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
from database.client import get_db, get_async_db
import schemas.department as department_schemas
import models.department as department_models


department_router = APIRouter()

#	get all departments
@department_router.get(
	'',
    response_model=List[department_schemas.Department],
    status_code=status.HTTP_200_OK
)
async def get_departments(db: Annotated[AsyncSession, Depends(get_async_db)]):
    query = await db.execute(
        select(department_models.Department)
	)
    return query.scalars().all()


#	create department
@department_router.post(
	'',
    response_model=department_schemas.Department,
    status_code=status.HTTP_201_CREATED
)
async def create_departments(
	department: department_schemas.DepartmentCreate,
	db: Annotated[AsyncSession, Depends(get_async_db)]
):
	query = await db.execute(
		insert(department_models.Department).
		values(**department.dict()).
		returning(department_models.Department)
	)
	department = query.scalar_one()
	await db.commit()
	await db.refresh(department)
	return department


#	get one department
@department_router.get(
	'/{id}',
    response_model=department_schemas.Department | None,
    status_code=status.HTTP_200_OK
)
async def retreive_departments(
	id: Annotated[int, Path(..., title='id of department to be retrieved')],
	db: Annotated[AsyncSession, Depends(get_async_db)]
):
	query = await db.execute(
		select(department_models.Department).where(
			department_models.Department.id == id
		)
	)
	if query:
		return query.scalar_one_or_none()
	raise HTTPException(
		detail="no department with given id",
		status_code=status.HTTP_404_NOT_FOUND
	)


#	update department
@department_router.put(
	'/{id}',
    response_model=department_schemas.Department,
)
async def update_departments(
	id: Annotated[int, Path(..., title='id of department to be updated')],
	department: department_schemas.DepartmentCreate,
	db: Annotated[AsyncSession, Depends(get_async_db)]
):
	query = await db.execute(
		update(department_models.Department).
        where(department_models.Department.id == id).
        values({**department.dict()}).
        returning(department_models.Department)
	)
	department = query.scalar_one()
	if not department:
		raise HTTPException(
		detail="no department with given id",
		status_code=status.HTTP_404_NOT_FOUND
	)
	await db.commit()
	await db.refresh(department)
	return department


#	delete department
@department_router.delete(
	'/{id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_departments(
	id: Annotated[int, Path(..., title='id of department to be updated')],
	db: Annotated[AsyncSession, Depends(get_async_db)]
):
	query = await db.execute(
		select(department_models.Department).where(
			department_models.Department.id == id
		)
	)
	if not query.scalar():
		raise HTTPException(
			detail="no department with given id",
			status_code=status.HTTP_404_NOT_FOUND
		)
	query = await db.execute(
		delete(department_models.Department).
        where(department_models.Department.id == id)
	)
	await db.commit()
	return