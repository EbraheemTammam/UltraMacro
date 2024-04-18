import uuid
from sqlalchemy import (
	Column,
	Integer,
	Float,
	String,
	Boolean,
	ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


class Student(Base):
	__tablename__ = 'students'
		
	id = Column(
	    UUID(as_uuid=True),
		primary_key=True,
		index=True,
		nullable=False,
		default=uuid.uuid4
	)
	name = Column(String(60), nullable=False)
	level = Column(Integer, nullable=False, default=1)
	registered_hours = Column(Integer, nullable=False, default=0)
	passed_hours = Column(Integer, nullable=False, default=0)
	excluded_hours = Column(Integer, nullable=False, default=0)
	research_hours = Column(Integer, nullable=False, default=0)
	total_points = Column(Float, nullable=False, default=0)
	gpa = Column(Float, nullable=False, default=0)
	total_mark = Column(Float, nullable=False, default=0)
	graduate = Column(Boolean, nullable=False, default=False)
	group_id = Column(
		Integer, 
		ForeignKey("divisions.id", ondelete="CASCADE"),
		nullable=False
	)
	division_id = Column(
		Integer, 
		ForeignKey("divisions.id", ondelete="CASCADE"),
		nullable=True
	)
	
	group = relationship('Division', foreign_keys=[group_id])
	division = relationship('Division', foreign_keys=[division_id])
	enrollments = relationship('Enrollment', back_populates='student')