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
import handlers.upload as upload_handlers


upload_router = APIRouter()



@upload_router.post('/upload_divisions')
async def upload_divisions(
    file: Annotated[UploadFile, File(...)],
    regulation: Annotated[int, Query(title='id of regulation')],
    db: Annotated[AsyncSession, Depends(get_async_db)]
):
    return await upload_handlers.division_upload(file, regulation, db)


@upload_router.post('/upload_courses')
async def upload_divisions(file: Annotated[UploadFile, File(...)], db: Annotated[AsyncSession, Depends(get_async_db)]):
    return await upload_handlers.course_upload(file, db)


@upload_router.post('/upload_enrollments')
async def upload_divisions(file: Annotated[UploadFile, File(...)], db: Annotated[AsyncSession, Depends(get_async_db)]):
    return await upload_handlers.enrollment_upload(file, db)