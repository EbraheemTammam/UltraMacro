from typing import Optional
from uuid import UUID

from sqlalchemy import func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


from generics.exceptions import EnrollmentNotFoundException, StudentNotFoundException, CourseNotFoundException


from .schemas import EnrollmentCreate, EnrollmentPartialUpdate
from .models import Enrollment

from course.models import Course
from student.models import Student
from division.models import Division
from user.models import User
from course.handler import CourseHandler



class EnrollmentHandler:


	def __init__(self, user: User, db: AsyncSession) -> None:
		self.user = user
		self.db = db
		self.course_handler = CourseHandler(user, db)
		self.NotFoundException = EnrollmentNotFoundException()
		self.retrieve_query = (
			select(Enrollment).
			options(
				selectinload(Enrollment.course)
			)
		)
		if not self.user.is_admin:
			self.retrieve_query = self.retrieve_query.where(
				Enrollment.student_id.in_(
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
		level: Optional[int] = None, 
		semester: Optional[int] = None,
		course_id: Optional[int] = None,
		only_passed: bool = False,
		excuse: bool = True,
	):
		query = self.retrieve_query
		if not excuse:
			query = query.where(Enrollment.grade!='عذر')
		if only_passed:
			query = query.where(
				or_(
					Enrollment.grade.in_(['A', 'B', 'C', 'D']),
					and_(
						Enrollment.grade=='بح',
						Enrollment.mark==0
					)
				)
			)
		if student_id:
			query = query.where(Enrollment.student_id==student_id)
		if level:
			query = query.where(
				Enrollment.course_id.in_(
					select(Course.id).
					where(Course.level==level)
				)
			)
		if semester:
			query = query.where(
				Enrollment.course_id.in_(
					select(Course.id).
					where(Course.semester==semester)
				)
			)
		if course_id:
			query = query.where(Enrollment.course_id==course_id)
		result = await self.db.execute(query)
		enrollments = result.scalars().all()
		return enrollments


	async def create(self, enrollment: EnrollmentCreate):
		student = await self.db.get(Student, enrollment.student_id)
		if not student:
			raise StudentNotFoundException()
		course = await self.db.get(Course, enrollment.course_id)
		if not course:
			raise CourseNotFoundException()
		new_enrollment = Enrollment(**enrollment.dict())
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
			enrollments = await self.get_all(student_id=student.id, course_id=course.id)
			count = len(enrollments) + 1
			if count > 2:
				student.excluded_hours += (count - 2) * course.credit_hours
			student.registered_hours += count * course.credit_hours
			student.passed_hours += course.credit_hours
			student.total_points += enrollment.points * course.credit_hours
			student.total_mark += (enrollments[0].mark + enrollments[-1].mark) / 2 if enrollments else enrollment.mark
		
		self.db.add(student)
		await self.db.commit()
		
		return 


	async def get_one(self, id: UUID):
		enrollment = await self.db.get(Enrollment, id)
		if enrollment:
			return enrollment
		raise self.NotFoundException


	async def get_or_create(
		self,
		headers: dict, 
		enrollment: dict, 
		student_id: UUID, 
		course_id: int,
	):
		#	check if enrollment exists
		level = int(headers.get('level')) if headers.get('level') else -1
		query = (
			select(Enrollment).
			where(
				and_(
					Enrollment.seat_id    == int(enrollment.get('seat_id')),
					Enrollment.level      == level,
					Enrollment.semester   == int(headers.get('semester')),
					Enrollment.year       == str(headers.get('year')),
					Enrollment.month      == str(headers.get('month')),
					Enrollment.mark       == float(enrollment.get('mark')),
					Enrollment.student_id == student_id,
					Enrollment.course_id  == course_id,
				)
			)
		)
		result = await self.db.execute(query)
		existing_enrollment = result.scalar()
		if existing_enrollment:
			return None
		#	if not, create one
		new_enrollment = Enrollment(
			**{
				'seat_id'   : int(enrollment['seat_id']),
				'level'     : int(headers['level']) if headers.get('level') else -1,
				'semester'  :  int(headers['semester']),
				'year'      : headers['year'],
				'month'     : headers['month'],
				'mark'      : float(enrollment['mark']),
				'full_mark' : int(enrollment['full_mark']),
				'grade'     :  enrollment['grade'],
				'points'    : float(enrollment['points']),
				'student_id': student_id,
				'course_id' : course_id,
			}
		)
		return new_enrollment


	async def update(self, id: UUID, enrollment: EnrollmentPartialUpdate):
		existing_enrollment = await self.get_one(id)
		for key, val in enrollment.dict().items():
			setattr(existing_enrollment, key, val)
		await self.db.commit()
		await self.db.refresh(existing_enrollment)
		return existing_enrollment


	async def delete(self, id: UUID):
		enrollment = await self.get_one(id)
		await self.db.delete(enrollment)
		await self.db.commit()
		return

