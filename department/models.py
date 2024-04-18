from sqlalchemy import (
	Column,
	Integer,
	String,
)
from sqlalchemy.orm import relationship

from database import Base


class Department(Base):
	__tablename__ = 'departments'

	id = Column(Integer, primary_key=True, index=True, nullable=False)
	name = Column(String(250), nullable=False)

	main_divisions = relationship(
		'Division', 
		back_populates='department_1',
		foreign_keys="[Division.department_1_id]"
	)
	secondary_divisions = relationship(
		'Division', 
		back_populates='department_2',
		foreign_keys="[Division.department_2_id]"
	)