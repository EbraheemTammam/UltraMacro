from typing import Annotated, List
from fastapi import (
	APIRouter,
	Response,
	status,
	Depends,
	Path,
	Query
)
from generics.permissions import CoursePermission

from .schemas import CourseCreate, Course
from .handler import CourseHandler


course_router = APIRouter()

#	get all courses
@course_router.get(
	'',
    response_model=List[Course],
    status_code=status.HTTP_200_OK
)
async def get_courses(
	permission_class: Annotated[CoursePermission, Depends(CoursePermission)],
	regulation: int = Query(None, title='id of regulation to filter result')
):
	handler = CourseHandler(permission_class.user, permission_class.db)
	return await handler.get_all(regulation)


#	create course
@course_router.post(
	'',
    response_model=Course,
    status_code=status.HTTP_201_CREATED
)
async def create_courses(
	course: CourseCreate,
	permission_class: Annotated[CoursePermission, Depends(CoursePermission)],
):
	handler = CourseHandler(permission_class.user, permission_class.db)
	return await handler.create(course)


#	get one course
@course_router.get(
	'/{id}',
    response_model=Course,
    status_code=status.HTTP_200_OK
)
async def retrieve_courses(
	id: Annotated[int, Path(..., title='id of course to be retrieved')],
	permission_class: Annotated[CoursePermission, Depends(CoursePermission)],
):
	await permission_class.check_permission(id)
	handler = CourseHandler(permission_class.user, permission_class.db)
	return await handler.get_one(id)


#	update course
@course_router.put(
	'/{id}',
    response_model=Course,
)
async def update_courses(
	id: Annotated[int, Path(..., title='id of course to be updated')],
	course: CourseCreate,
	permission_class: Annotated[CoursePermission, Depends(CoursePermission)],
):
	await permission_class.check_permission(id)
	handler = CourseHandler(permission_class.user, permission_class.db)
	return await handler.update(id, course)


#	delete course
@course_router.delete(
	'/{id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_courses(
	id: Annotated[int, Path(..., title='id of course to be updated')],
	permission_class: Annotated[CoursePermission, Depends(CoursePermission)],
):
	await permission_class.check_permission(id)
	handler = CourseHandler(permission_class.user, permission_class.db)
	await handler.get_one(id)
	return await handler.delete(id)
	