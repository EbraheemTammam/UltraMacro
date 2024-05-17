import uuid
from sqlalchemy import (
	Column,
	Integer,
	Float,
	String,
	ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


class Enrollment(Base):
	__tablename__ = 'enrollments'
		
	id = Column(
	    UUID(as_uuid=True),
	    primary_key=True,
	    index=True,
	    nullable=False,
	    default=uuid.uuid4
	)
	seat_id = Column(Integer, nullable=False)
	level = Column(Integer)
	semester = Column(Integer)
	year = Column(String(4), nullable=False)
	month = Column(String(10), nullable=False)
	points = Column(Float, nullable=False)
	mark = Column(Float, nullable=False)
	full_mark = Column(Integer, nullable=False)
	grade = Column(String(3), nullable=False)
	student_id = Column(
		UUID(as_uuid=True),
		ForeignKey("students.id", ondelete="CASCADE"),
		nullable=False
	) 
	course_id = Column(
		Integer,
		ForeignKey("courses.id", ondelete="CASCADE"),
		nullable=False
	)
	
	student = relationship("Student", back_populates="enrollments")
	course = relationship("Course")