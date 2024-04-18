from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings



engine = create_engine(
	settings.DATABASE_URL,
	#connect_args={'check_same_thread': False}, # uncomment if using sqlite,
	future=True # for using the new async orm
)

SessionLocal = sessionmaker(
	autocommit=False,
	autoflush=False,
	bind=engine,
	future=True
)

def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()
