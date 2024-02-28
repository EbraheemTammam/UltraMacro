from typing import Annotated from pydantic import BaseModel


class TokenPayload(BaseModel):
	user_id: int
