from fastapi import HTTPException, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete, and_
from sqlalchemy.orm import selectinload

from schemas import (
	division as division_schemas,
)
from models import (
    division as division_models,
	course as course_models,
	student as student_models,
	enrollment as enrollment_models,
)
from handlers import (
    xl as xl_handlers,
	department as department_handlers,
	division as division_handlers,
	student as student_handlers,
	course as course_handlers,
	enrollment as enrollment_handlers,
)


async def division_upload(file: UploadFile, regulation_id: int, db: AsyncSession):
	content = await file.read()
	data = await xl_handlers.extract_divisions(content)
	for d in data:
		d['regulation_id'] = regulation_id
		d['regulation_id'] = 1
		try:
			d1 = await department_handlers.get_department_by_name(d['department_1_id'], db)
			d['department_1_id'] = d1.id
		except:
			d['department_1_id'] = None
		try:
			d2 = await department_handlers.get_department_by_name(d['department_2_id'], db)
			d['department_2_id'] = d2.id
		except:
			d['department_2_id'] = None
		division = division_models.Division(**d)
		db.add(division)
	await db.commit()
	return data


async def course_upload(file: UploadFile, db: AsyncSession):
	content = await file.read()
	data = await xl_handlers.extract_courses(content)
	for d in data:
		course = course_models.Course(**{key: value for key, value in d.items() if key != 'division'})
		db.add(course)
		division = await division_handlers.get_division_by_name(d['division'], db)
		course.divisions.append(division)
	await db.commit()
	return data


async def enrollment_upload(file: UploadFile, db: AsyncSession):
	content = await file.read()
	data = await xl_handlers.final_dict(content)
	division = await division_handlers.get_division_by_name(data['headers']['division'], db)
	response = []
	for d in data['content']:
		student = await student_handlers.get_student_by_name_and_division(d['student'], division, db)
		if not student:
			response.append({'student': d['student'], 'course': d['course'], 'status': 'first year data does not exist'})
			continue
		try:
			course = await course_handlers.get_course_by_code_and_divisions(d['code'], [student.group, student.division], db)
		except:
			try:
				course = await course_handlers.get_course_by_code(d['code'], db)
			except:
				response.append({'student': student.name, 'course': d['course'], 'status': 'course is not in the database'})
				continue
		enrollment = await enrollment_handlers.enrollment_get_or_create(data['headers'], d, student, course, db)
		if not enrollment:
			response.append({'student': student.name, 'course': course.name, 'status': 'enrollment already exists'})
			continue
		db.add(enrollment)
		#		post create login goes here
		response.append({'student': student.name, 'course': course.name, 'status': 'successfully added'})
	await db.commit()
	return data['headers']