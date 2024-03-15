from uuid import UUID
from typing import Any
from fastapi import HTTPException, status, Depends
from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from authentication.oauth2 import get_current_user
from database import get_async_db
from exceptions import ForbiddenException

from models.user import User, UserDivisions
from models.division import Division
from models.student import Student
from models.course import Course, CourseDivisions



class Permission:

	def __init__(self, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)) -> None:
		self.user = user
		self.db = db
		self.ForbiddenException = ForbiddenException()

	async def has_object_permission(self, id: Any) -> bool:
		pass


	async def check_permission(self, id: Any):
		if not await self.has_object_permission(id):
			raise self.ForbiddenException



class RegulationPermission(Permission):

	async def has_object_permission(self, id):
		if self.user.is_admin:
			return True
		query = await self.db.execute(
			select(Division).
			where(
				and_(
					Division.regulation_id==id,
					Division.users.any(id=self.user.id)
				)
			).
			exists()
		)
		return query


class DepartmentPermission(Permission):

	async def has_object_permission(self, id):
		query = await self.db.execute(
			select(Division).
			where(
				and_(
					or_(
						Division.department_1_id==id,
						Division.department_2_id==id
					),
					Division.users.any(id=self.user.id)
				)
			).
			exists()
		)
		return query


class DivisionPermission(Permission):

	async def has_object_permission(self, id):
		query = await self.db.execute(
			select(Division).
			where(
				and_(
					Division.id==id,
					Division.users.any(id=self.user.id)
				)
			).
			exists()
		)
		return query


class StudentPermission(Permission):

	async def has_object_permission(self, id):
		query = await self.db.execute(
			select(Division).
			where(
				and_(
					or_(
						Division.id==(
							select(Student.group_id).
							where(Student.id==id)
						),
						Division.id==(
							select(Student.group_id).
							where(Student.id==id)
						)
					),
					Division.users.any(id=self.user.id)
				)
			).
			exists()
		)
		return query
	

class CoursePermission(Permission):

	async def has_object_permission(self, id):
		query = await self.db.execute(
			select(Division).
			where(
				and_(
					Division.courses.any(id=id),
					Division.users.any(id=self.user.id)
				)
			).
			exists()
		)
		return query
	


class EnrollmentPermission(Permission):

	async def has_object_permission(self, id):
		pass