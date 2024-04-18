from sqlalchemy import (
	Column,
	Integer,
	String,
)
from sqlalchemy.orm import relationship

from database import Base


class Regulation(Base):
    __tablename__ = 'regulations'
    
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String(250), nullable=False)
    max_gpa = Column(Integer, nullable=False)

    divisions = relationship("Division", back_populates="regulation")