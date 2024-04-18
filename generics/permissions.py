from typing import Any
from fastapi import Depends
from sqlalchemy import and_, or_, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from authentication.oauth2 import get_current_user
from database import get_async_db
from .exceptions import ForbiddenException, UnAuthorizedException

from user.models import User, UserDivisions
from division.models import Division
from student.models import Student
from course.models import CourseDivisions
from enrollment.models import Enrollment



class AdminPermission:

	def __init__(self, user: User = Depends(get_current_user)) -> None:
		if not user.is_admin:
			raise UnAuthorizedException()
		self.user = user
		


class Permission:

	def __init__(self, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_async_db)) -> None:
		self.user = user
		self.db = db
		self.ForbiddenException = ForbiddenException()

	async def has_object_permission(self, id: Any) -> bool:
		pass


	async def check_permission(self, id: Any):
		if not (self.user.is_admin or await self.has_object_permission(id)):
			raise self.ForbiddenException



class RegulationPermission(Permission):

	async def has_object_permission(self, id: Any) -> bool:
		query = await self.db.execute(
			select(exists(Division)).
			where(
				and_(
					Division.regulation_id==id,
					Division.users.any(id=self.user.id)
				)
			)
		)
		return query.scalar()


class DepartmentPermission(Permission):

	async def has_object_permission(self, id: Any) -> bool:
		query = await self.db.execute(
			select(exists(Division)).
			where(
				and_(
					or_(
						Division.department_1_id==id,
						Division.department_2_id==id
					),
					Division.users.any(id=self.user.id)
				)
			)
		)
		return query.scalar()


class DivisionPermission(Permission):

	async def has_object_permission(self, id: Any) -> bool:
		query = await self.db.execute(
			select(exists(Division)).
			where(
				and_(
					Division.id==id,
					Division.users.any(id=self.user.id)
				)
			)
		)
		return query.scalar()


class StudentPermission(Permission):

	async def has_object_permission(self, id: Any) -> bool:
		query = await self.db.execute(
			select(exists(Division)).
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
			)
		)
		return query.scalar()
	

class CoursePermission(Permission):

	async def has_object_permission(self, id: Any) -> bool:
		query = await self.db.execute(
			select(exists(Division)).
			where(
				and_(
					Division.courses.any(id=id),
					Division.users.any(id=self.user.id)
				)
			)
		)
		return query.scalar()
	


class EnrollmentPermission(Permission):

	async def has_object_permission(self, id: Any) -> bool:
		enrollment = await self.db.get(Enrollment, id)
		return await CoursePermission().has_object_permission(enrollment.course_id)