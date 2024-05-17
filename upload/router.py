from typing import Annotated, List

from fastapi import (
	APIRouter,
	Depends,
	Query,
    File, 
    UploadFile,
    status,
    BackgroundTasks
)
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_db

from generics.permissions import AdminPermission

from .handler import UploadHandler
from .schemas import DivisionUploadResponse, CourseUploadResponse, EnrollmentUploadResponse


upload_router = APIRouter()



@upload_router.post(
    '/upload_divisions',
    status_code=status.HTTP_201_CREATED,
    response_model=List[DivisionUploadResponse]
)
async def upload_divisions(
    permission_class: Annotated[AdminPermission, Depends(AdminPermission)],
    db: Annotated[AsyncSession, Depends(get_async_db)],
    regulation: Annotated[int, Query(title='id of regulation')],
    file: Annotated[UploadFile, File(...)]
):
    handler = UploadHandler(permission_class.user, db, file)
    return await handler.division_upload(regulation)


@upload_router.post(
    '/upload_courses', 
    status_code=status.HTTP_201_CREATED,
    response_model=List[CourseUploadResponse]
)
async def upload_courses(
    permission_class: Annotated[AdminPermission, Depends(AdminPermission)],
    db: Annotated[AsyncSession, Depends(get_async_db)],
    regulation: Annotated[int, Query(title='id of regulation')],
    file: Annotated[UploadFile, File(...)]
):
    handler = UploadHandler(permission_class.user, db, file)
    return await handler.course_upload()


@upload_router.post(
    '/upload_enrollments', 
    status_code=status.HTTP_201_CREATED,
    response_model=List[EnrollmentUploadResponse]
)
async def upload_enrollments(
    permission_class: Annotated[AdminPermission, Depends(AdminPermission)], 
    db: Annotated[AsyncSession, Depends(get_async_db)],
    file: Annotated[UploadFile, File(...)],
    background_tasks: BackgroundTasks
):
    handler = UploadHandler(permission_class.user, db, file, background_tasks)
    return await handler.enrollment_upload()