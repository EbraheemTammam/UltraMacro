from typing import Annotated, List
from fastapi import (
	APIRouter,
	Response,
	status,
	Depends,
	Path,
	Query,
    File,
    UploadFile,
)

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