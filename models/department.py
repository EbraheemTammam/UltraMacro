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


class Department(Base):
	__tablename__ = 'departments'

	id = Column(Integer, primary_key=True, index=True, nullable=False)
	name = Column(String(250), nullable=False)