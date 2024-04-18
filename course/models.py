import uuid
from sqlalchemy import (
	Table,
	Column,
	Integer,
	String,
	Boolean,
	ForeignKey,
)
from sqlalchemy.orm import relationship

from database import Base



CourseDivisions = Table(
	'course_divisions', 
	Base.metadata,
    Column(
		'course_id',
		Integer,
		ForeignKey("courses.id", ondelete="CASCADE"),
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

    divisions = relationship("Division", secondary=CourseDivisions, back_populates='courses')


