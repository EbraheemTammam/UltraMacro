import uuid
import enum
from sqlalchemy import (
	Table,
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
from sqlalchemy_utils import EmailType, URLType, PasswordType

from database import Base


class User(Base):
	__tablename__ = 'users'
    
	id = Column(
		UUID(as_uuid=True),
		primary_key=True,
		index=True,
		default=uuid.uuid4,
		nullable=False
	)
	first_name = Column(String(50), nullable=False)
	last_name = Column(String(50), nullable=False)
	email = Column(EmailType, unique=True, nullable=False)
	password = Column(
		PasswordType(schemes=['bcrypt'], deprecated="auto"),
		nullable=False
	)
	is_admin = Column(Boolean, nullable=False, default=False)

	divisions = relationship("Division", secondary="UserDivision")


UserDivision = Table(
	'user_divisions', 
	Base.metadata,
    Column(
		'user_id',
		UUID(as_uuid=True),
		ForeignKey("users.id", ondelete="CASCADE"),
		primary_key=True,
		index=True,
		nullable=False,
		default=uuid.uuid4
	),
    Column(
		'division_id',
		Integer,
		ForeignKey("divisions.id", ondelete="CASCADE"),
		primary_key=True,
		index=True,
		nullable=False,
	)
)