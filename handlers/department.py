from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete
from sqlalchemy.orm import selectinload


import schemas.department as department_schemas
import models.department as department_models





async def get_all_departments(db: AsyncSession):
    query = await db.execute(
        select(department_models.Department)
	)
    return query.scalars().all()


async def create_department(department: department_schemas.DepartmentCreate, db: AsyncSession):
    query = await db.execute(
    	insert(department_models.Department).
    	values(**department.dict()).
    	returning(department_models.Department)
    )
    department = query.scalar_one()
    await db.commit()
    await db.refresh(department)
    return department


async def get_one_department(id: int, db: AsyncSession):
    query = await db.execute(
    	select(department_models.Department).where(
    		department_models.Department.id == id
    	)
    )
    department = query.scalar()
    if department:
        return department
    raise HTTPException(
    	detail="no department with given id",
    	status_code=status.HTTP_404_NOT_FOUND
    )


async def update_department(id: int, department: department_schemas.DepartmentCreate, db: AsyncSession):
    query = await db.execute(
    	update(department_models.Department).
        where(department_models.Department.id == id).
        values({**department.dict()}).
        returning(department_models.Department)
    )
    department = query.scalar()
    if not department:
        raise HTTPException(
        detail="no department with given id",
        status_code=status.HTTP_404_NOT_FOUND
    )
    await db.commit()
    await db.refresh(department)
    return department


async def delete_department(id: int, db: AsyncSession):
    await get_one_department(id, db)
    await db.execute(
    	delete(department_models.Department).
        where(department_models.Department.id == id)
    )
    await db.commit()
    return