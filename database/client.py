from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings


engine = create_engine(
	settings.DATABASE_URL,
	connect_args={'check_same_thread': False}, # uncomment if using sqlite,
	future=True # for using the new async orm
)

async_engine = create_async_engine(
	settings.ASYNC_DATABASE_URL,
	connect_args={'check_same_thread': False}, # uncomment if using sqlite,
	future=True # for using the new async orm
)


SessionLocal = sessionmaker(
	autocommit=False,
	autoflush=False,
	bind=engine,
	future=True
)

AsyncSessionLocal = sessionmaker(
	async_engine,
	autocommit=False,
	autoflush=False,
	class_=AsyncSession,
	expire_on_commit=False,
)


Base = declarative_base()

def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

async def get_async_db():
	async with AsyncSessionLocal() as db:
		try:
			yield db
		except Exception as e:
			await db.rollback()
			raise e
		finally:
			await db.close()

