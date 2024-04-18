from uuid import UUID
from typing import Annotated
from fastapi import (
	APIRouter,
	status,
	Depends,
	Path,
	Query
)

from generics.permissions import EnrollmentPermission

from .schemas import EnrollmentPartialUpdate, Enrollment
from .handler import EnrollmentHandler


enrollment_router = APIRouter()



@enrollment_router.patch(
    '/{id}',
    response_model=Enrollment
)
async def partial_update_enrollments(
	id: UUID, 
	enrollment: EnrollmentPartialUpdate, 
	permission_class: Annotated[EnrollmentPermission, Depends(EnrollmentPermission)]
):
	handler = EnrollmentHandler(permission_class.user, permission_class.db)
	return await handler.update(id, enrollment)



@enrollment_router.delete(
    '/{id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def update_enrollments(
	id: UUID, 
	permission_class: Annotated[EnrollmentPermission, Depends(EnrollmentPermission)]
):
    handler = EnrollmentHandler(permission_class.user, permission_class.db)
    return await handler.delete(id)