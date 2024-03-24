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



class Token(Base):
	__tablename__ = 'tokens'
		
	user_id = Column(
        UUID(as_uuid=True),
		ForeignKey('users.id', ondelete='CASCADE'),
		nullable=False
	)
	token = Column(String(255), primary_key=True, nullable=False)
	valid = Column(Boolean, nullable=False, default=True)

	user = relationship('User', uselist=False)