from uuid import UUID
from typing import Annotated 
from pydantic import BaseModel


class Token(BaseModel):
	token_type: str
	token: str

class TokenPayload(BaseModel):
	user_id: UUID
