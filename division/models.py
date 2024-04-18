from sqlalchemy import (
	Column,
	Integer,
	String,
	Boolean,
	ForeignKey,
)
from sqlalchemy.orm import relationship

from database import Base
from user.models import UserDivisions
from course.models import CourseDivisions


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
		foreign_keys=[department_1_id],
		back_populates='main_divisions'
	)
	department_2 = relationship(
		"Department", 
		foreign_keys=[department_2_id],
		back_populates='secondary_divisions'
	)
	users = relationship("User", secondary=UserDivisions, back_populates='divisions')
	courses = relationship("Course", secondary=CourseDivisions, back_populates='divisions')