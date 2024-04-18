from typing import Annotated 
from fastapi import (
	APIRouter,
	Depends,
	Path,
	Query
)

from .oauth2 import TokenHandler, get_current_user
from . import schemas as auth_schemas
from user.models import User


authentication_router = APIRouter()


@authentication_router.post(
    '/login',
    response_model=auth_schemas.Token,
)
async def login(
    #credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
	credentials: auth_schemas.Login,
    token_handler: Annotated[TokenHandler, Depends(TokenHandler)]
):
	return await token_handler.validate(credentials)


@authentication_router.post(
	'/login/verify'
)
async def verify(accessToken: auth_schemas.Verify, token_handler: Annotated[TokenHandler, Depends(TokenHandler)]):
	token = await token_handler.verify(accessToken.accessToken)
	return {"key": accessToken.accessToken, "user": token}



@authentication_router.post('/logout')
async def logout(user: Annotated[User, Depends(get_current_user)], token_handler: Annotated[TokenHandler, Depends(TokenHandler)]):
	await token_handler.invalidate(user)
	return {'detail': 'logged out successfully'}