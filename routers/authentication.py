from typing import Annotated 
from fastapi import (
	APIRouter,
	Response,
	status,
	HTTPException,
	Depends,
	Path,
	Query
)
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from authentication.oauth2 import create_access_token
from authentication.utils import verify_password
from database import get_db, get_async_db
import schemas.authentication as auth_schemas
import models.user as user_models


authentication_router = APIRouter()


@authentication_router.post(
    '/login',
    response_model=auth_schemas.Token,
)
async def login(
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_async_db)]
):
	query = await db.execute(
		select(user_models.User).
		where(user_models.User.email == credentials.username)
	)
	user = query.scalar()
	e = HTTPException(
		detail="Invalid credentials",
		status_code=status.HTTP_403_FORBIDDEN
	)
	if not user or credentials.password != user.password:
		raise e
	token = create_access_token(payload={"user_id": str(user.id)})
	return {"token_type": "bearer", "token": token}