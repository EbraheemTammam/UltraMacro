from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, and_, func
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete
from sqlalchemy.orm import selectinload


from generics.exceptions import StudentNotFoundException


from .schemas import StudentCreate

from student.models import Student
from division.models import Division
from course.models import Course
from enrollment.models import Enrollment
from user.models import User
from division.handler import DivisionHandler
from enrollment.handler import EnrollmentHandler
from course.handler import CourseHandler



class StudentHandler:


	def __init__(self, user: User, db: AsyncSession) -> None:
		self.user = user
		self.db = db
		self.NotFoundException = StudentNotFoundException()
		self.division_handler = DivisionHandler(user, db)
		self.enrollment_handler = EnrollmentHandler(user, db)
		self.course_handler = CourseHandler(user, db)
		self.retrieve_query = (
			select(Student).
			options(
				selectinload(Student.group).
				options(
					selectinload(Division.regulation),
					selectinload(Division.department_1),
					selectinload(Division.department_2),
				),
				selectinload(Student.division).
				options(
					selectinload(Division.regulation),
					selectinload(Division.department_1),
					selectinload(Division.department_2),
				)
			)
		)
		if not self.user.is_admin:
			self.retrieve_query = self.retrieve_query.where(
				or_(
					Student.division_id.in_(
						select(Division.id).
						where(Division.users.any(id=self.user.id))
					),
					Student.group_id.in_(
						select(Division.id).
						where(Division.users.any(id=self.user.id))
					)
				)
			)


	async def get_all(self, regulation_id: int | None, graduate: bool = False):
		query = self.retrieve_query
		if regulation_id:
			query = query.where(
				or_(
					Student.group_id.in_(
						select(Division.id).
						where(Division.regulation_id==regulation_id)
					),
					Student.division_id.in_(
						select(Division.id).
						where(Division.regulation_id==regulation_id)
					)
				)
			)
		if graduate:
			query = query.where(Student.graduate == True)
		students = await self.db.execute(query)
		return students.scalars().all()
		


	async def create(self, student: StudentCreate):
		await self.division_handler.get_one(student.group_id)
		if student.division_id:
			await self.division_handler.get_one(student.division_id)
		query = await self.db.execute(
			insert(Student).
			values(**student.dict()).
			returning(Student).
			options(
				selectinload(Student.group).
				options(
					selectinload(Division.regulation),
					selectinload(Division.department_1),
					selectinload(Division.department_2),
				),
				selectinload(Student.division).
				options(
					selectinload(Division.regulation),
					selectinload(Division.department_1),
					selectinload(Division.department_2),
				)
			)
		)
		student = query.scalar_one()
		await self.db.commit()
		await self.db.refresh(student)
		return student


	async def get_one(self, id: UUID):
		query = self.retrieve_query.where(Student.id==id)
		query = await self.db.execute(query)
		student = query.scalar()
		if student:
			return student
		raise self.NotFoundException


	async def get_by_name(self, name: str):
		query = self.retrieve_query.where(Student.name==name)
		query = await self.db.execute(query)
		student = query.scalar()
		return student


	async def get_by_name_and_division(self, name: str, division: Division):
		student = await self.get_by_name(name)
		if student:
			if division.group or division.private:
				return student
			student.division = division
		else:
			if division.group or division.private:
				student = Student(
					name=name, 
					group_id=division.id, 
					excluded_hours=0, 
					passed_hours=0, 
					registered_hours=0, 
					research_hours=0,
					total_points=0,
					total_mark=0
				)
				self.db.add(student)
				await self.db.commit()
				await self.db.refresh(student)
		return student


	async def update(self, id: UUID, student: StudentCreate):
		await self.division_handler.get_one(student.group_id)
		if student.division_id:
			await self.division_handler.get_one(student.division_id)
		query = (
			update(Student).
			where(Student.id == id).
			values({**student.dict()}).
			returning(Student).
			options(
				selectinload(Student.group).
				options(
					selectinload(Division.regulation),
					selectinload(Division.department_1),
					selectinload(Division.department_2),
				),
				selectinload(Student.division).
				options(
					selectinload(Division.regulation),
					selectinload(Division.department_1),
					selectinload(Division.department_2),
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
		await self.db.execute(
			delete(Student).
			where(Student.id == id)
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
			select(func.sum(Enrollment.points * Course.credit_hours)).
			join(Course).
			where(
				and_(
					Enrollment.grade.in_(['A', 'B', 'C', 'D']),
					Enrollment.student_id==student_id,
					Enrollment.course_id.in_(
						select(Course.id).
						where(
							and_(
								Course.level==level,
								Course.semester==semester
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
	

	async def check_graduation(self, student: Student):
		group = await self.db.get(Division, student.group_id)
		division = await self.db.get(Division, student.division_id)
		if group.group and not division:
			return False
		passed_enrollments = await self.enrollment_handler.get_all(student.id, None, None, None, True, False)
		if await self.course_handler.check_required_and_not_passed(group.id, passed_enrollments):
			return False
		elif division:
			if await self.course_handler.check_required_and_not_passed(division.id, passed_enrollments):
				return False
		if student.gpa < 1:
			return False
		return True
	

	async def post_add_enrollment(self, student: Student):
		#	check level
		if student.passed_hours > 98:
			student.level = 4
		elif student.passed_hours > 62:
			student.level = 3
		elif student.passed_hours > 28:
			student.level = 2
		#	check graduation
		if student.level == 4:
			group = await self.db.get(Division, student.group_id)
			division = await self.db.get(Division, student.division_id)
			if group.private and (student.passed_hours < group.hours):
				return
			elif (not student.division) or (student.passed_hours < division.hours):
				return
			student.graduate = await self.check_graduation(student)
		student.gpa = await self.calculate_gpa(student)
		self.db.add(student)
		await self.db.commit()
		return
	

	async def calculate_gpa(self, student: Student):
		denominator = student.registered_hours - student.excluded_hours - student.research_hours
		return student.total_points / denominator if denominator else 0