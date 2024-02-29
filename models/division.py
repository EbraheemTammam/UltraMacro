import uuid
import enum
from sqlalchemy import (
	Column,
	Integer,
	String,
	Boolean,
	ForeignKey,
	Enum,
	Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text, null
from sqlalchemy_utils import EmailType, URLType

from database.client import Base


class Division(Base):
	__tablename__ = 'divisions'
    
	id = Column(Integer, primary_key=True, index=True, nullable=False)
	name = Column(String(250), nullable=False)
	private = Column(Boolean, nullable=False, default=False)
	group = Column(Boolean, nullable=False, default=False)
	hours = Column(Integer, nullable=False, default=0)
	regulation_id = Column(
		Integer,
		ForeignKey("regulations.id", ondelete="CASCADE"),
		nullable=False
	)
	department_1_id = Column(
		Integer,
		ForeignKey("departments.id", ondelete="CASCADE"),
		nullable=True
	)
	department_2_id = Column(
		Integer,
		ForeignKey("departments.id", ondelete="CASCADE"),
		nullable=True
	)

	regulation = relationship("Regulation", back_populates="divisions")
	department_1 = relationship(
		"Department", 
		foreign_keys=[department_1_id]
	)
	department_2 = relationship(
		"Department", 
		foreign_keys=[department_2_id]
	)