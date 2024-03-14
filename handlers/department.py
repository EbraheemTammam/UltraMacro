from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete
from sqlalchemy.orm import selectinload


import schemas.department as department_schemas
from models import (
    department as department_models,
    user as user_models,
    division as division_models
)




async def get_all_departments(user: user_models.User, db: AsyncSession):
    query = select(department_models.Department)
    if not user.is_admin:
        query = query.where(
            or_(
                department_models.Department.id.in_(
                    select(division_models.Division.department_1_id).
                    where(division_models.Division.users.any(id=user.id))
                ),
                department_models.Department.id.in_(
                    select(division_models.Division.department_2_id).
                    where(division_models.Division.users.any(id=user.id))
                )
            )
        )
        print(query)
    divisions = await db.execute(query)
    return divisions.scalars().all()


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
    department = await db.get(department_models.Department, id)
    if department:
        return department
    raise HTTPException(
    	detail=f"no department with given id: {id}",
    	status_code=status.HTTP_404_NOT_FOUND
    )


async def get_department_by_name(name: str, db: AsyncSession):
    query = await db.execute(
        select(department_models.Department).
        where(department_models.Department.name==name)
    )
    department = query.scalar()
    if department:
        return department
    raise HTTPException(
    	detail=f"no department with given name: {name}",
    	status_code=status.HTTP_404_NOT_FOUND
    )

async def update_department(id: int, department: department_schemas.DepartmentCreate, db: AsyncSession):
    query = (
    	update(department_models.Department).
        where(department_models.Department.id == id).
        values({**department.dict()}).
        returning(department_models.Department)
    )
    department = await db.execute(query)
    department = department.scalar()
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