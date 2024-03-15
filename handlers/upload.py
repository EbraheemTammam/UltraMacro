import asyncio
from fastapi import HTTPException, status, UploadFile, File, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete, and_
from sqlalchemy.orm import selectinload


from authentication.oauth2 import get_current_user
from database import get_async_db


from schemas import (
	division as division_schemas,
)
from models import (
    division as division_models,
	course as course_models,
	student as student_models,
	enrollment as enrollment_models,
	user as user_models
)
from handlers import xl as xl_handlers
from handlers.department import DepartmentHandler
from handlers.division import DivisionHandler
from handlers.student import StudentHandler
from handlers.course import CourseHandler
from handlers.enrollment import EnrollmentHandler



class UploadHandler:


	def __init__(
		self,
		file: UploadFile = File(...),
		user: user_models.User = Depends(get_current_user), 
		db: AsyncSession = Depends(get_async_db),
		department_handler: DepartmentHandler = Depends(DepartmentHandler),
		division_handler: DivisionHandler = Depends(DivisionHandler),
		student_handler: StudentHandler = Depends(StudentHandler),
		course_handler: CourseHandler = Depends(CourseHandler),
		enrollment_handler: EnrollmentHandler = Depends(EnrollmentHandler)
	) -> None:
		self.file = file
		self.user = user
		self.db = db
		self.department_handler = department_handler
		self.division_handler = division_handler
		self.student_handler = student_handler
		self.course_handler = course_handler
		self.enrollment_handler = enrollment_handler


	async def division_upload(self, regulation_id: int):
		content = await self.file.read()
		data = await xl_handlers.extract_divisions(content)
		for d in data:
			d['regulation_id'] = regulation_id
			d['regulation_id'] = 1
			try:
				d1 = await self.department_handler.get_by_name(d['department_1_id'])
				d['department_1_id'] = d1.id
			except:
				d['department_1_id'] = None
			try:
				d2 = await self.department_handler.get_by_name(d['department_2_id'])
				d['department_2_id'] = d2.id
			except:
				d['department_2_id'] = None
			division = division_models.Division(**d)
			self.db.add(division)
		await self.db.commit()
		return data


	async def course_upload(self):
		content = await self.file.read()
		data = await xl_handlers.extract_courses(content)
		for d in data:
			course = course_models.Course(**{key: value for key, value in d.items() if key != 'division'})
			self.db.add(course)
			division = await self.division_handler.get_by_name(d['division'])
			course.divisions.append(division)
		await self.db.commit()
		return data


	async def enrollment_upload(self):
		content = await self.file.read()
		data = await xl_handlers.final_dict(content)
		division = await self.division_handler.get_by_name(data['headers']['division'])
		response = []
		students = set()
		for d in data['content']:
			student = await self.student_handler.get_by_name_and_division(d['student'], division)
			if not student:
				response.append({'student': d['student'], 'course': d['course'], 'status': 'first year data does not exist'})
				continue
			students.add(student)
			try:
				course = await self.course_handler.get_by_code_and_divisions(d['code'], [student.group, student.division])
			except:
				try:
					course = await self.course_handler.get_by_code(d['code'])
				except:
					response.append({'student': student.name, 'course': d['course'], 'status': 'course is not in the database'})
					continue
			enrollment = await self.enrollment_handler.get_or_create(data['headers'], d, student, course)
			if not enrollment:
				response.append({'student': student.name, 'course': course.name, 'status': 'enrollment already exists'})
				continue
			self.db.add(enrollment)
			await self.enrollment_handler.post_create(enrollment, student, course)
			response.append({'student': student.name, 'course': course.name, 'status': 'successfully added'})
		for student in students:
			await self.student_handler.post_add_enrollment(student)
		await self.db.commit()
		return response