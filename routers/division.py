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
from database import get_db, get_async_db
import schemas.division as division_schemas
from models import (
	division as division_models,
	regulation as regulation_models,
	department as department_models,
	user as user_models
)


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
    query = await db.execute(
        select(division_models.Division).
		options(
			selectinload(division_models.Division.regulation),
			selectinload(division_models.Division.department_1),
			selectinload(division_models.Division.department_2),
		)
	)
    return query.scalars().all()


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
	regulation = await db.execute(
		select(regulation_models.Regulation).
		where(regulation_models.Regulation.id == division.regulation_id)
	)
	if not regulation.scalar():
		raise HTTPException(
			detail=f"no regulation with given id: {division.regulation_id}",
			status_code=status.HTTP_400_BAD_REQUEST
		)
	department_1 = await db.execute(
		select(department_models.Department).
		where(department_models.Department.id == division.department_1_id)
	)
	if not department_1.scalar():
		raise HTTPException(
			detail=f"no department with given id: {division.department_1_id}",
			status_code=status.HTTP_400_BAD_REQUEST
		)
	if division.department_2_id:
		department_2 = await db.execute(
			select(department_models.Department).
			where(department_models.Department.id == division.department_2_id)
		)
		if not department_2.scalar():
			raise HTTPException(
				detail=f"no department with given id: {division.department_2_id}",
				status_code=status.HTTP_400_BAD_REQUEST
			)
	query = await db.execute(
		insert(division_models.Division).
		values(**division.dict()).
		returning(division_models.Division).
		options(
			selectinload(division_models.Division.regulation),
			selectinload(division_models.Division.department_1),
			selectinload(division_models.Division.department_2),
		)
	)
	division = query.scalar_one()
	await db.commit()
	await db.refresh(division)
	return division


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
	query = await db.execute(
		select(division_models.Division).
		where(division_models.Division.id == id).
		options(
			selectinload(division_models.Division.regulation),
			selectinload(division_models.Division.department_1),
			selectinload(division_models.Division.department_2),
		)
	)
	division = query.scalar()
	if division:
		return division
	raise HTTPException(
		detail="no division with given id",
		status_code=status.HTTP_404_NOT_FOUND
	)


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
	regulation = await db.execute(
		select(regulation_models.Regulation).
		where(regulation_models.Regulation.id == division.regulation_id)
	)
	if not regulation.scalar():
		raise HTTPException(
			detail=f"no regulation with given id: {division.regulation_id}",
			status_code=status.HTTP_400_BAD_REQUEST
		)
	department_1 = await db.execute(
		select(department_models.Department).
		where(department_models.Department.id == division.department_1_id)
	)
	if not department_1.scalar():
		raise HTTPException(
			detail=f"no department with given id: {division.department_1_id}",
			status_code=status.HTTP_400_BAD_REQUEST
		)
	if division.department_2_id:
		department_2 = await db.execute(
			select(department_models.Department).
			where(department_models.Department.id == division.department_2_id)
		)
		if not department_2.scalar():
			raise HTTPException(
				detail=f"no department with given id: {division.department_2_id}",
				status_code=status.HTTP_400_BAD_REQUEST
			)
	query = await db.execute(
		update(division_models.Division).
        where(division_models.Division.id == id).
        values({**division.dict()}).
        returning(division_models.Division).
		options(
			selectinload(division_models.Division.regulation),
			selectinload(division_models.Division.department_1),
			selectinload(division_models.Division.department_2),
		)
	)
	division = query.scalar()
	if not division:
		raise HTTPException(
		detail="no division with given id",
		status_code=status.HTTP_404_NOT_FOUND
	)
	await db.commit()
	await db.refresh(division)
	return division


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
	query = await db.execute(
		select(division_models.Division).where(
			division_models.Division.id == id
		)
	)
	if not query.scalar():
		raise HTTPException(
			detail="no division with given id",
			status_code=status.HTTP_404_NOT_FOUND
		)
	query = await db.execute(
		delete(division_models.Division).
        where(division_models.Division.id == id)
	)
	await db.commit()
	return