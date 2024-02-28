from sqlalchemy import (
	Column,
	Integer,
	String,
)

from database.client import Base


class Regulation(Base):
    __tablename__ = 'regulations'
    
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String(250), nullable=False)