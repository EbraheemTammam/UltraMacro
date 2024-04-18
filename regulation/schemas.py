from typing import Annotated
from pydantic import BaseModel


class RegulationBase(BaseModel):
    name: str
    max_gpa: int

class RegulationCreate(RegulationBase):
    pass

class Regulation(RegulationBase):
    id: int

    class Config:
        from_attributes = True