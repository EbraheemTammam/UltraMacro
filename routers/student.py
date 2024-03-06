from uuid import UUID
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
import schemas.student as student_schemas
import models.student as student_models
import models.division as division_models


student_router = APIRouter()

#	get all students
@student_router.get(
	'',
    response_model=List[student_schemas.Student],
    status_code=status.HTTP_200_OK
)
async def get_students(db: Annotated[AsyncSession, Depends(get_async_db)]):
    query = await db.execute(
        select(student_models.Student).
		options(
			selectinload(student_models.Student.group).
			options(
				selectinload(division_models.Division.regulation),
				selectinload(division_models.Division.department_1),
				selectinload(division_models.Division.department_2),
			),
			selectinload(student_models.Student.division).
			options(
				selectinload(division_models.Division.regulation),
				selectinload(division_models.Division.department_1),
				selectinload(division_models.Division.department_2),
			)
		)
	)
    return query.scalars().all()

#	get all graduate students
@student_router.get(
	'/graduates',
    response_model=List[student_schemas.Student],
    status_code=status.HTTP_200_OK
)
async def get_graduate_students(db: Annotated[AsyncSession, Depends(get_async_db)]):
    query = await db.execute(
        select(student_models.Student).
		where(student_models.Student.graduate == True).
		options(
			selectinload(student_models.Student.group).
			options(
				selectinload(division_models.Division.regulation),
				selectinload(division_models.Division.department_1),
				selectinload(division_models.Division.department_2),
			),
			selectinload(student_models.Student.division).
			options(
				selectinload(division_models.Division.regulation),
				selectinload(division_models.Division.department_1),
				selectinload(division_models.Division.department_2),
			)
		)
	)
    return query.scalars().all()


#	create student
@student_router.post(
	'',
    response_model=student_schemas.Student,
    status_code=status.HTTP_201_CREATED
)
async def create_students(
	student: student_schemas.StudentCreate,
	db: Annotated[AsyncSession, Depends(get_async_db)]
):
	group = await db.execute(
		select(division_models.Division).
		where(division_models.Division.id == student.group_id)
	)
	if not group.scalar():
		raise HTTPException(
			detail=f"no group with given id: {student.group_id}",
			status_code=status.HTTP_400_BAD_REQUEST
		)
	if student.division_id:
		division = await db.execute(
			select(division_models.Division).
			where(division_models.Division.id == student.division_id).
			options(
				selectinload(student_models.Student.group).
				options(
					selectinload(division_models.Division.regulation),
					selectinload(division_models.Division.department_1),
					selectinload(division_models.Division.department_2),
				),
				selectinload(student_models.Student.division).
				options(
					selectinload(division_models.Division.regulation),
					selectinload(division_models.Division.department_1),
					selectinload(division_models.Division.department_2),
				)
			)
		)
		if not division.scalar():
			raise HTTPException(
				detail=f"no division with given id: {student.division_id}",
				status_code=status.HTTP_400_BAD_REQUEST
			)
	query = await db.execute(
		insert(student_models.Student).
		values(**student.dict()).
		returning(student_models.Student).
		options(
			selectinload(student_models.Student.group).
			options(
				selectinload(division_models.Division.regulation),
				selectinload(division_models.Division.department_1),
				selectinload(division_models.Division.department_2),
			),
			selectinload(student_models.Student.division).
			options(
				selectinload(division_models.Division.regulation),
				selectinload(division_models.Division.department_1),
				selectinload(division_models.Division.department_2),
			)
		)
	)
	student = query.scalar_one()
	await db.commit()
	await db.refresh(student)
	return student


#	get one student
@student_router.get(
	'/{id}',
    response_model=student_schemas.Student | None,
    status_code=status.HTTP_200_OK
)
async def retreive_students(
	id: Annotated[UUID, Path(..., title='id of student to be retrieved')],
	db: Annotated[AsyncSession, Depends(get_async_db)]
):
	query = await db.execute(
		select(student_models.Student).where(
			student_models.Student.id == id
		).
		options(
			selectinload(student_models.Student.group).
			options(
				selectinload(division_models.Division.regulation),
				selectinload(division_models.Division.department_1),
				selectinload(division_models.Division.department_2),
			),
			selectinload(student_models.Student.division).
			options(
				selectinload(division_models.Division.regulation),
				selectinload(division_models.Division.department_1),
				selectinload(division_models.Division.department_2),
			)
		)
	)
	student = query.scalar()
	if student:
		return student
	raise HTTPException(
		detail="no student with given id",
		status_code=status.HTTP_404_NOT_FOUND
	)


#	update student
@student_router.put(
	'/{id}',
    response_model=student_schemas.Student,
)
async def update_students(
	id: Annotated[UUID, Path(..., title='id of student to be updated')],
	student: student_schemas.StudentCreate,
	db: Annotated[AsyncSession, Depends(get_async_db)]
):
	group = await db.execute(
		select(division_models.Division).
		where(division_models.Division.id == student.group_id)
	)
	if not group.scalar():
		raise HTTPException(
			detail=f"no group with given id: {student.group_id}",
			status_code=status.HTTP_400_BAD_REQUEST
		)
	if student.division_id:
		division = await db.execute(
			select(division_models.Division).
			where(division_models.Division.id == student.division_id)
		)
		if not division.scalar():
			raise HTTPException(
				detail=f"no division with given id: {student.division_id}",
				status_code=status.HTTP_400_BAD_REQUEST
			)
	query = await db.execute(
		update(student_models.Student).
        where(student_models.Student.id == id).
        values({**student.dict()}).
        returning(student_models.Student).
		options(
			selectinload(student_models.Student.group).
			options(
				selectinload(division_models.Division.regulation),
				selectinload(division_models.Division.department_1),
				selectinload(division_models.Division.department_2),
			),
			selectinload(student_models.Student.division).
			options(
				selectinload(division_models.Division.regulation),
				selectinload(division_models.Division.department_1),
				selectinload(division_models.Division.department_2),
			)
		)
	)
	student = query.scalar()
	if not student:
		raise HTTPException(
		detail="no student with given id",
		status_code=status.HTTP_404_NOT_FOUND
	)
	await db.commit()
	await db.refresh(student)
	return student


#	delete student
@student_router.delete(
	'/{id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_students(
	id: Annotated[UUID, Path(..., title='id of student to be updated')],
	db: Annotated[AsyncSession, Depends(get_async_db)]
):
	query = await db.execute(
		select(student_models.Student).where(
			student_models.Student.id == id
		)
	)
	if not query.scalar():
		raise HTTPException(
			detail="no student with given id",
			status_code=status.HTTP_404_NOT_FOUND
		)
	query = await db.execute(
		delete(student_models.Student).
        where(student_models.Student.id == id)
	)
	await db.commit()
	return