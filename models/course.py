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

from database import Base



class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    code = Column(String(10), nullable=False)
    name = Column(String(60), nullable=False)
    lecture_hours = Column(Integer, nullable=False)
    practical_hours = Column(Integer, nullable=False)
    credit_hours = Column(Integer, nullable=False)
    level = Column(Integer, nullable=False)
    semester = Column(Integer, nullable=False)
    required = Column(Boolean, nullable=False)