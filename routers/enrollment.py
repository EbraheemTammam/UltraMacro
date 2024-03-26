from uuid import UUID
from typing import Annotated, List
from fastapi import (
	APIRouter,
	Response,
	status,
	HTTPException,
	Depends,
	Path,
	Query
)
from schemas.enrollment import EnrollmentPartialUpdate, Enrollment

from handlers.enrollment import EnrollmentHandler


enrollment_router = APIRouter()



@enrollment_router.patch(
    '/{id}',
    response_model=Enrollment
)
async def partial_update_enrollments(id: UUID, enrollment: EnrollmentPartialUpdate, handler: Annotated[EnrollmentHandler, Depends(EnrollmentHandler)]):
	return await handler.update(id, enrollment)



@enrollment_router.delete(
    '/{id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def update_enrollments(id: UUID, handler: Annotated[EnrollmentHandler, Depends(EnrollmentHandler)]):
    return await handler.delete(id)