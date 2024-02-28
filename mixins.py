from datetime import datetime

from sqlalchemy import Column, Datetime
from sqlalchemy.orm import declarative_mixin

@declarative_mixin
class Timestamp:
	created_at = Column(Datetime, default=datetime.utcnow, nullable=False)
	updated_at = Column(Datetime, default=datetime.utcnow, nullable=False)
