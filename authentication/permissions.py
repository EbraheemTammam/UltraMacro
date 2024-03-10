from uuid import UUID
from typing import Any
from fastapi import HTTPException, status
from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


import models



async def has_regulation_permission(
	user: models.user.User, 
	object_id: int, 
	auth_exception: HTTPException, 
	db = AsyncSession
):
	query = (
		select(models.division.Division).
		where(
			and_(
				models.division.Division.regulation_id==object_id,
				models.division.Division.id.in_(
					select(models.user.UserDivisions.columns.division_id).
					where(models.user.UserDivisions.columns.user_id==user.id)
				)
			)
		)
	)
	result = await db.execute(query)
	divisions = result.scalars().all()
	if divisions:
		return
	raise auth_exception

async def has_department_permission(
	user: models.user.User, 
	object_id: int, 
	auth_exception: HTTPException, 
	db: AsyncSession
):
	query = (
		select(models.division.Division).
		where(
			and_(
				or_(
					models.division.Division.department_1_id==object_id,
					models.division.Division.department_2_id==object_id
				),
				models.division.Division.id.in_(
					select(models.user.UserDivisions.columns.division_id).
					where(models.user.UserDivisions.columns.user_id==user.id)
				)
			)
		)
	)
	result = await db.execute(query)
	divisions = result.scalars().all()
	if divisions:
		return
	raise auth_exception


async def has_division_permission(
	user: models.user.User, 
	object_id: int, 
	auth_exception: HTTPException, 
	db: AsyncSession
):
	query = (
		select(models.division.Division).
		where(
			and_(
				models.division.Division.id==object_id,
				models.division.Division.id.in_(
					select(models.user.UserDivisions.columns.division_id).
					where(models.user.UserDivisions.columns.user_id==user.id)
				)
			)
		)
	)
	result = await db.execute(query)
	divisions = result.scalars().all()
	if divisions:
		return
	raise auth_exception


async def has_student_permission(
	user: models.user.User, 
	object_id: int, 
	auth_exception: HTTPException, 
	db: AsyncSession
):
	query = (
		select(models.division.Division).
		where(
			and_(
				or_(
					models.division.Division.id==select(
						models.student.Student.group_id
					).where(models.student.Student.id==object_id),
					models.division.Division.id==select(
						models.student.Student.group_id
					).where(models.student.Student.id==object_id)
				),
				models.division.Division.id.in_(
					select(models.user.UserDivisions.columns.division_id).
					where(models.user.UserDivisions.columns.user_id==user.id)
				)
			)
		)
	)
	query = await db.execute(query)
	if query.scalars().all():
		return
	raise auth_exception


async def has_course_permission(
	user: models.user.User, 
	object_id: int, 
	auth_exception: HTTPException, 
	db: AsyncSession
):
	query = (
		select(models.division.Division).
		where(
			and_(
				models.division.Division.id.in_(
					select(models.course.CourseDivisions.columns.division_id).
					where(models.course.CourseDivisions.columns.course_id==object_id)
				),
				models.division.Division.id.in_(
					select(models.user.UserDivisions.columns.division_id).
					where(models.user.UserDivisions.columns.user_id==user.id)
				)
			)
		)
	)
	query = await db.execute(query)
	if query.scalars().all():
		return
	raise auth_exception


async def has_permission(
	user: models.user.User, 
	class_: Any, 
	object_id: int | UUID, 
	db: AsyncSession
) -> None:
	#	main exception
	auth_exception = HTTPException(
		detail="User has no permission",
		status_code=status.HTTP_401_UNAUTHORIZED
	)
	#	admin always allowed
	if user.is_admin:
		return
	#	check regulation
	if class_ == models.regulation.Regulation:
		await has_regulation_permission(user, object_id, auth_exception, db)
	#	check department
	elif class_ == models.department.Department:
		await has_department_permission(user, object_id, auth_exception, db)
	#	check division
	if class_ == models.division.Division:
		await has_division_permission(user, object_id, auth_exception, db)
	#	check student
	elif class_ == models.student.Student:
		await has_student_permission(user, object_id, auth_exception, db)
	#	check course
	elif class_ == models.course.Course:
		await has_course_permission(user, object_id, auth_exception, db)