from typing import Optional
from uuid import UUID
from fastapi import Depends
from sqlalchemy import String, cast, func, and_, or_
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete
from sqlalchemy.orm import selectinload


from exceptions import EnrollmentNotFoundException, StudentNotFoundException, CourseNotFoundException
from authentication.permissions import EnrollmentPermission


import schemas.enrollment as enrollment_schemas
from models.enrollment import Enrollment
from models.course import Course
from models.student import Student
from models.division import Division

from handlers.course import CourseHandler



class EnrollmentHandler:


	def __init__(
		self, 
		permission_class: EnrollmentPermission = Depends(EnrollmentPermission),
		course_handler: CourseHandler = Depends(CourseHandler)
	) -> None:
		self.user = permission_class.user
		self.db = permission_class.db
		self.permission_class = permission_class
		self.course_handler = course_handler
		self.model = Enrollment
		self.NotFoundException = EnrollmentNotFoundException()
		self.retrieve_query = (
			select(self.model).
			options(
				selectinload(self.model.course)
			)
		)
		if not self.user.is_admin:
			self.retrieve_query = self.retrieve_query.where(
				self.model.student_id.in_(
					select(Student.id).
					where(
						or_(
							Student.group_id.in_(
								select(Division.id).
								where(Division.users.any(id=self.user.id))
							),
							Student.division_id.in_(
								select(Division.id).
								where(Division.users.any(id=self.user.id))
							)
						)
					)
				)
			)

	
	async def get_all(
		self,
		student_id: Optional[UUID], 
		level: Optional[int], 
		semester: Optional[int],
		course_id: Optional[int],
		only_passed: bool = False,
		excuse: bool = True,
	):
		query = self.retrieve_query
		if not excuse:
			query = query.where(self.model.grade!='عذر')
		if only_passed:
			query = query.where(
				or_(
					self.model.grade.in_(['A', 'B', 'C', 'D']),
					and_(
						self.model.grade=='بح',
						self.model.mark==0
					)
				)
			)
		if student_id:
			query = query.where(self.model.student_id==student_id)
		if level:
			query = query.where(
				self.model.course_id.in_(
					select(Course.id).
					where(Course.level==level)
				)
			)
		if semester:
			query = query.where(
				self.model.course_id.in_(
					select(Course.id).
					where(Course.semester==semester)
				)
			)
		if course_id:
			query = query.where(self.model.course_id==course_id)
		result = await self.db.execute(query)
		enrollments = result.scalars().all()
		return enrollments


	async def create(self, enrollment: enrollment_schemas.EnrollmentCreate):
		student = await self.db.get(Student, enrollment.student_id)
		if not student:
			raise StudentNotFoundException()
		course = await self.db.get(Course, enrollment.course_id)
		if not course:
			raise CourseNotFoundException()
		new_enrollment = self.model(**enrollment.dict())
		self.db.add(new_enrollment)
		await self.db.commit()
		await self.db.refresh(new_enrollment)
		return new_enrollment
	

	async def post_create(self, enrollment: Enrollment, student: Student, course: Course):
		if course.credit_hours == 0: return student
		#   check if research
		if enrollment.grade == 'بح' and enrollment.mark == 0:
			student.research_hours += course.credit_hours
			student.passed_hours += course.credit_hours
			student.registered_hours += course.credit_hours
		#   check if passed course
		elif enrollment.grade in ['A', 'B', 'C', 'D']:
			enrollments = await self.get_all(student.id, None, None, course.id)
			count = len(enrollments) + 1
			if count > 2:
				student.excluded_hours += (count - 2) * course.credit_hours
			student.registered_hours += count * course.credit_hours
			student.passed_hours += course.credit_hours
			student.total_points += enrollment.points * course.credit_hours
			student.total_mark += (enrollments[0].mark + enrollments[-1].mark) / 2 if enrollments else enrollment.mark
		return student


	async def get_one(self, id: UUID):
		await self.permission_class.check_permission(id)
		enrollment = await self.db.get(self.model, id)
		if enrollment:
			return enrollment
		raise self.NotFoundException


	async def get_or_create(
		self,
		headers: dict, 
		enrollment: dict, 
		student: Student, 
		course: Course,
	):
		#	check if enrollment exists
		query = (
			select(self.model).
			where(
				and_(
					self.model.seat_id==enrollment.get('seat_id'),
					self.model.level==headers.get('level'),
					self.model.semester==headers.get('semester'),
					self.model.year==headers.get('year'),
					self.model.month==headers.get('month'),
					self.model.mark==enrollment.get('mark'),
					self.model.student_id==student.id,
					self.model.course_id==course.id,
				)
			)
		)
		result = await self.db.execute(query)
		existing_enrollment = result.scalar()
		if existing_enrollment:
			return None
		#	if not, create one
		new_enrollment = self.model(
			**{
				'seat_id': enrollment['seat_id'],
				'level': headers['level'],
				'semester': headers['semester'],
				'year': headers['year'],
				'month': headers['month'],
				'mark': float(enrollment['mark']),
				'full_mark': enrollment['full_mark'],
				'grade': enrollment['grade'],
				'points': (
					(float(enrollment['mark']) / (course.credit_hours * 10)) - 5 
					if enrollment['grade'] in ['A', 'B', 'C', 'D'] and course.credit_hours != 0
					else 0
				),
				'student_id': student.id,
				'course_id': course.id,
			}
		)
		return new_enrollment


	async def update(self, id: UUID, enrollment: enrollment_schemas.EnrollmentCreate):
		existing_enrollment = self.get_one(id)
		for key, val in enrollment.dict().items():
			setattr(existing_enrollment, key, val)
		await self.permission_class.check_permission(id)
		await self.db.commit()
		await self.db.refresh(existing_enrollment)
		return existing_enrollment


	async def delete(self, id: UUID):
		enrollment = await self.get_one(id)
		await self.db.delete(enrollment)
		await self.db.commit()
		return

