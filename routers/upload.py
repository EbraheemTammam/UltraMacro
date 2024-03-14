from typing import Annotated, List
from fastapi import (
	APIRouter,
	Response,
	status,
	HTTPException,
	Depends,
	Path,
	Query,
    File,
    UploadFile,
)
from sqlalchemy.ext.asyncio import AsyncSession
from authentication.oauth2 import get_current_user
from database import get_db, get_async_db

from handlers.upload import UploadHandler


upload_router = APIRouter()



@upload_router.post('/upload_divisions')
async def upload_divisions(
    handler: Annotated[UploadHandler, Depends(UploadHandler)],
    regulation: Annotated[int, Query(title='id of regulation')]
):
    return await handler.division_upload(regulation)


@upload_router.post('/upload_courses')
async def upload_courses(handler: Annotated[UploadHandler, Depends(UploadHandler)]):
    return await handler.course_upload()


@upload_router.post('/upload_enrollments')
async def upload_enrollments(handler: Annotated[UploadHandler, Depends(UploadHandler)]):
    return await handler.enrollment_upload()