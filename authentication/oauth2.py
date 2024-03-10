from typing import Annotated 
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from config import settings
from database import get_async_db
from models import (
    user as user_models,
	division as division_models
)
import schemas



oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.TOKEN_URL)



def create_access_token(payload: dict):
	data = payload.copy()
	expires = datetime.utcnow() + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
	data.update({'exp': expires})

	token = jwt.encode(
		data,
		settings.SECRET_KEY,
		algorithm=settings.TOKEN_ENCODING_ALGORITHM,
	)
	return token

def verify_access_token(token: str, credentials_exceoption):
	try:
		payload = jwt.decode(
			token,
			settings.SECRET_KEY,
			algorithms=[settings.TOKEN_ENCODING_ALGORITHM]
		)
		id: str = payload.get('user_id')
		if not id:
			raise credentials_exceoption
	except JWTError:
		raise credentials_exceoption
	return schemas.authentication.TokenPayload(**payload)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[AsyncSession, Depends(get_async_db)]):
	credentials_exceoption = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail='could not validate credentials',
		headers={'WWW-Authenticate': 'Bearer'}
	)
	token = verify_access_token(token, credentials_exceoption)
	user = await db.execute(
		select(user_models.User).
		where(user_models.User.id==token.user_id).
		options(
			selectinload(user_models.User.divisions).
			options(
				selectinload(division_models.Division.regulation),
				selectinload(division_models.Division.department_1),
				selectinload(division_models.Division.department_2),
			)
		)
	)
	user = user.scalar_one()
	return user
