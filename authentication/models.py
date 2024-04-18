from sqlalchemy import (
	Column,
	String,
	Boolean,
	ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

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