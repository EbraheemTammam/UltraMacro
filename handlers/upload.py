from fastapi import HTTPException, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, update, delete
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
)


async def division_upload(file: UploadFile, db: AsyncSession):
	content = await file.read()
	data = await xl_handlers.extract_divisions(content)
	for d in data:
		d['department_1_id'] = await department_handlers.get_department_by_name(d['department_1_id']).id
		d['department_2_id'] = await department_handlers.get_department_by_name(d['department_2_id']).id
		division = division_models.Division(d)
		db.add(division)
	await db.commit()
	return data


async def course_upload(file: UploadFile, db: AsyncSession):
	content = await file.read()
	data = await xl_handlers.extract_courses(content)
	for d in data:
		course = course_models.Course({key: value for key, value in d.items() if key != 'division'})
		db.add(course)
		division = await division_handlers.get_division_by_name(d['division'], db)
		course.divisions.append(division)
	await db.commit()
	return data


async def enrollment_upload(file: UploadFile, db: AsyncSession):
	content = await file.read()
	data = await xl_handlers.final_dict(content)
	division = await division_handlers.get_division_by_name(data['headers']['division'])
	response = []
	for d in data['content']:
		student = await student_handlers.get_student_by_name_and_division(d['student'], division, db)
		if not student:
			response.append({'student': d['student'], 'course': d['course'], 'status': 'first year data does not exist'})
			continue
		# try:
		# 	student = await student_handlers.get_student_by_name(d['student'], db)
		# 	if not (division.group or division.private):
		# 		student.division = division
		# except:
		# 	if not (division.group or division.private):
		# 		response.append({'student': d['student'], 'course': d['course'], 'status': 'first year data does not exist'})
		# 		continue
		# 	student = student_models.Student(name=d['student'])
		# finally:
		# 	db.add(student)
		# 	await db.commit()
		# 	await db.refresh(student)
		try:
			course = await course_handlers.get_course_by_code_and_divisions(d['code'], [student.group, student.division], db)
		except:
			try:
				course = await course_handlers.get_course_by_code(d['code'], db)
			except:
				response.append({'student': student.name, 'course': d['course'], 'status': 'course is not in the database'})
				continue
		enrollment = enrollment_models.Enrollment(
			{
				'seat_id': d['seat_id'],
				'level': data['headers']['level'],
				'semester': data['headers']['semester'],
				'year': data['headers']['year'],
				'month': data['headers']['month'],
				'mark': d['mark'],
				'full_mark': d['full_mark'],
				'grade': d['grade'],
				'points': (
					(int(d['mark']) / (course.credit_hours * 10)) - 5 
					if d['grade'] in ['A', 'B', 'C', 'D'] and course.credit_hours != 0
					else 0
				),
				'student_id': student.id,
				'course_id': course.id,
			}
		)
		db.add(enrollment)
		response.append({'student': student.name, 'course': course.name, 'status': 'successfully added'})
	await db.commit()
	return data['headers']