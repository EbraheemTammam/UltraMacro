from typing import Annotated 
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from generics.exceptions import UnAuthorizedException
from config import settings
from database import get_async_db
from user.models import User

from .models import Token
from .schemas import TokenPayload, Login



oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.TOKEN_URL)


def create_access_token(payload: dict):
	data = payload.copy()

	token = jwt.encode(
		data,
		settings.SECRET_KEY,
		algorithm=settings.TOKEN_ENCODING_ALGORITHM,
	)
	return token


class TokenHandler:


	def __init__(self, db: AsyncSession = Depends(get_async_db)) -> None:
		self.db = db
		self.credentials_exception = UnAuthorizedException(detail="Invalid credentials")


	async def create(self, user: User):
		payload = {
			'user_id': str(user.id),
			'is_admin': user.is_admin
		}
		#expires = datetime.utcnow() + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
		#payload.update({'exp': expires})

		token = jwt.encode(
			payload,
			settings.SECRET_KEY,
			algorithm=settings.TOKEN_ENCODING_ALGORITHM,
		)

		token = Token(user_id=user.id, token=token)
		self.db.add(token)
		await self.db.commit()

		return token


	async def verify(self, token: str):
		user_token = await self.db.get(Token, token)
		if not (user_token and user_token.valid):
			raise self.credentials_exception
		try:
			payload = jwt.decode(
				token,
				settings.SECRET_KEY,
				algorithms=[settings.TOKEN_ENCODING_ALGORITHM]
			)
			id: str = payload.get('user_id')
			if not id:
				raise self.credentials_exception
		except JWTError:
			raise self.credentials_exception
		return TokenPayload(**payload)
	

	async def validate(self, credentials: Login):
		query = await self.db.execute(
			select(User).
			where(User.email == credentials.email)
		)
		user = query.scalar()
		if not user or credentials.password != user.password:
			raise self.credentials_exception
		query = await self.db.execute(
			select(Token).where(Token.user_id==user.id)
		)
		token = query.scalar()
		if not token:
			raise self.credentials_exception
		token.valid = True
		self.db.add(token)
		await self.db.commit()
		return {"token_type": "bearer", "accessToken": token.token}


	async def invalidate(self, user: User):
		query = await self.db.execute(
			select(Token).where(Token.user_id==user.id)
		)
		token = query.scalar()
		if not token:
			raise self.credentials_exception
		token.valid = False
		self.db.add(token)
		await self.db.commit()


async def get_current_user(
	token: Annotated[str, Depends(oauth2_scheme)], 
	token_handler: Annotated[TokenHandler, Depends(TokenHandler)]
):
	token = await token_handler.verify(token)
	user = await token_handler.db.get(User, token.user_id)
	return user
