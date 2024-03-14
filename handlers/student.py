from typing import Optional
from uuid import UUID
from fastapi import HTTPException, status, Depends
from sqlalchemy import or_, and_, func, String, cast
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete, String
from sqlalchemy.orm import selectinload


from authentication.oauth2 import get_current_user
from database import get_async_db
from exceptions import StudentNotFoundException


import schemas.student as student_schemas
from models import (
	student as student_models,
	division as division_models,
	user as user_models,
	enrollment as enrollment_models,
	course as course_models
)
from handlers.division import DivisionHandler
from handlers.enrollment import EnrollmentHandler
from handlers.course import CourseHandler



class StudentHandler:


	def __init__(
		self, 
		user: user_models.User = Depends(get_current_user), 
		db: AsyncSession = Depends(get_async_db),
		division_handler: DivisionHandler = Depends(DivisionHandler),
		enrollment_handler: EnrollmentHandler = Depends(EnrollmentHandler),
		course_handler: CourseHandler = Depends(CourseHandler)
	) -> None:
		self.user = user
		self.db = db
		self.NotFoundException = StudentNotFoundException()
		self.model = student_models.Student
		self.division_handler = division_handler
		self.enrollment_handler = enrollment_handler
		self.course_handler = course_handler
		self.retrieve_query = (
			select(self.model).
			options(
				selectinload(self.model.group).
				options(
					selectinload(division_models.Division.regulation),
					selectinload(division_models.Division.department_1),
					selectinload(division_models.Division.department_2),
				),
				selectinload(self.model.division).
				options(
					selectinload(division_models.Division.regulation),
					selectinload(division_models.Division.department_1),
					selectinload(division_models.Division.department_2),
				)
			)
		)
		if not user.is_admin:
			self.retrieve_query = self.retrieve_query.where(
				or_(
					self.model.division_id.in_(
						select(division_models.Division.id).
						where(division_models.Division.users.any(id=user.id))
					),
					self.model.group_id.in_(
						select(division_models.Division.id).
						where(division_models.Division.users.any(id=user.id))
					)
				)
			)


	async def get_all(self, regulation_id: int | None, graduate: bool = False):
		query = self.retrieve_query
		if regulation_id:
			query = query.where(
				or_(
					self.model.group_id.in_(
						select(division_models.Division.id).
						where(division_models.Division.regulation_id==regulation_id)
					),
					self.model.division_id.in_(
						select(division_models.Division.id).
						where(division_models.Division.regulation_id==regulation_id)
					)
				)
			)
		if graduate:
			query = query.where(self.model.graduate == True)
		students = await self.db.execute(query)
		return students.scalars().all()
		


	async def create(self, student: student_schemas.StudentCreate):
		await self.division_handler.get_one(student.group_id)
		if student.division_id:
			await self.division_handler.get_one(student.division_id)
		query = await self.db.execute(
			insert(self.model).
			values(**student.dict()).
			returning(self.model).
			options(
				selectinload(self.model.group).
				options(
					selectinload(division_models.Division.regulation),
					selectinload(division_models.Division.department_1),
					selectinload(division_models.Division.department_2),
				),
				selectinload(self.model.division).
				options(
					selectinload(division_models.Division.regulation),
					selectinload(division_models.Division.department_1),
					selectinload(division_models.Division.department_2),
				)
			)
		)
		student = query.scalar_one()
		await self.db.commit()
		await self.db.refresh(student)
		return student


	async def get_one(self, id: UUID):
		query = self.retrieve_query.where(self.model.id==id)
		query = await self.db.execute(query)
		student = query.scalar()
		if student:
			return student
		raise self.NotFoundException


	async def get_by_name(self, name: str):
		query = self.retrieve_query.where(self.model.name==name)
		query = await self.db.execute(query)
		student = query.scalar()
		if student:
			return student
		raise self.NotFoundException


	async def get_by_name_and_division(self, name: str, division: division_models.Division):
		try:
			student = await self.get_by_name(name)
			if not (division.group or division.private):
				student.division = division
		except:
			if not (division.group or division.private):
				return None
			student = self.model(name=name, group_id=division.id)
			self.db.add(student)
		await self.db.commit()
		await self.db.refresh(student)
		return student


	async def update(self, id: UUID, student: student_schemas.StudentCreate):
		await self.division_handler.get_one(student.group_id)
		if student.division_id:
			await self.division_handler.get_one(student.division_id)
		query = (
			update(self.model).
			where(self.model.id == id).
			values({**student.dict()}).
			returning(self.model).
			options(
				selectinload(self.model.group).
				options(
					selectinload(division_models.Division.regulation),
					selectinload(division_models.Division.department_1),
					selectinload(division_models.Division.department_2),
				),
				selectinload(self.model.division).
				options(
					selectinload(division_models.Division.regulation),
					selectinload(division_models.Division.department_1),
					selectinload(division_models.Division.department_2),
				)
			)
		)
		query = await self.db.execute(query)
		student = query.scalar()
		if not student:
			raise self.NotFoundException
		await self.db.commit()
		await self.db.refresh(student)
		return student


	async def delete(self, id: UUID):
		await self.get_one(id)
		await self.db.execute(
			delete(self.model).
			where(self.model.id == id)
		)
		await self.db.commit()
		return
	

	async def get_semester_detail(
		self,
		student_id: Optional[UUID], 
		level: Optional[int], 
		semester: Optional[int],
	):
		enrollments = await self.enrollment_handler.get_all(student_id, level, semester, None)
		total_points_query = (
			select(func.sum(enrollment_models.Enrollment.points * course_models.Course.credit_hours)).
			join(course_models.Course).
			where(
				and_(
					enrollment_models.Enrollment.grade.in_(['A', 'B', 'C', 'D']),
					enrollment_models.Enrollment.student_id==cast(str(student_id), String),
					enrollment_models.Enrollment.course_id.in_(
						select(course_models.Course.id).
						where(
							and_(
								course_models.Course.level==level,
								course_models.Course.semester==semester
							)
						)
					)
				)
			)
		)
		result = await self.db.execute(total_points_query)
		points = result.scalar()
		return {'level': level, 'semester': semester, 'points': points, 'enrollments': enrollments}


	async def get_student_detail(self, id: UUID):
		student = await self.get_one(id)
		details = [await self.get_semester_detail(id, l, s) for l in range(1, 5) for s in range(1, 4)]
		return {
			'regulation': student.division.regulation.name if student.division else student.group.regulation.name,
			'department_1': (
				student.division.department_1.name 
				if student.division and student.division.department_1
				else (
					student.group.department_1.name
					if student.group.department_1
					else None
				)
			),
			'department_2': (
				student.division.department_2.name 
				if student.division and student.division.department_2
				else (
					student.group.department_2.name
					if student.group.department_2
					else None
				)
			),
			'group': student.group.name,
			'division': student.division.name if student.division else None,
			**{key: val for key, val in student.__dict__.items() if key not in ['group', 'division']}, 
			'details': details
		}
	

	async def check_graduation(self, student: student_models.Student):
		group = await self.db.get(division_models.Division, student.group_id)
		division = await self.db.get(division_models.Division, student.division_id)
		if group.group and not division:
			return False
		passed_enrollments = self.enrollment_handler.get_all(student.id, None, None, None, True, False)
		if self.course_handler.check_required_and_not_passed(group.id, passed_enrollments):
			return False
		elif division:
			if self.course_handler.check_required_and_not_passed(division.id, passed_enrollments):
				return False
		if student.gpa < 1:
			return False
		return True
	

	async def post_add_enrollment(self, student: student_models.Student):
		#	check level
		if student.passed_hours > 98:
			student.level = 4
		elif student.passed_hours > 62:
			student.level = 3
		elif student.passed_hours > 28:
			student.level = 2
		#	check graduation
		if student.level < 4:
			return
		group = await self.db.get(division_models.Division, student.group_id)
		division = await self.db.get(division_models.Division, student.division_id)
		if group.private and (student.passed_hours < group.hours):
			return
		elif (not student.division) or (student.passed_hours < division.hours):
			return
		student.graduate = self.check_graduation(student)
		self.db.add(student)
		await self.db.commit()
		return