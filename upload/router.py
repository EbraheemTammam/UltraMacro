from typing import Annotated

from fastapi import (
	APIRouter,
	Depends,
	Query,
    File, 
    UploadFile,
)
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_db

from generics.permissions import AdminPermission

from .handler import UploadHandler


upload_router = APIRouter()



@upload_router.post('/upload_divisions')
async def upload_divisions(
    permission_class: Annotated[AdminPermission, Depends(AdminPermission)],
    db: Annotated[AsyncSession, Depends(get_async_db)],
    regulation: Annotated[int, Query(title='id of regulation')],
    file: Annotated[UploadFile, File(...)]
):
    handler = UploadHandler(permission_class.user, db, file)
    return await handler.division_upload(regulation)


@upload_router.post('/upload_courses')
async def upload_courses(
    permission_class: Annotated[AdminPermission, Depends(AdminPermission)],
    db: Annotated[AsyncSession, Depends(get_async_db)],
    regulation: Annotated[int, Query(title='id of regulation')],
    file: Annotated[UploadFile, File(...)]
):
    handler = UploadHandler(permission_class.user, db, file)
    return await handler.course_upload()


@upload_router.post('/upload_enrollments')
async def upload_enrollments(
    permission_class: Annotated[AdminPermission, Depends(AdminPermission)], 
    db: Annotated[AsyncSession, Depends(get_async_db)],
    file: Annotated[UploadFile, File(...)]
):
    handler = UploadHandler(permission_class.user, db, file)
    return await handler.enrollment_upload()