from uuid import UUID
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
	token_type: str
	accessToken: str

class TokenPayload(BaseModel):
	user_id: UUID
	is_admin: bool

class Login(BaseModel):
	email: EmailStr
	password: str

class Verify(BaseModel):
	accessToken: str