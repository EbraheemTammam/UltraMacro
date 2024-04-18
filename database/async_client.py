from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import settings



async_engine = create_async_engine(
	settings.ASYNC_DATABASE_URL,
	#connect_args={'check_same_thread': False}, # uncomment if using sqlite,
	future=True # for using the new async orm
)

AsyncSessionLocal = sessionmaker(
	async_engine,
	autocommit=False,
	autoflush=False,
	class_=AsyncSession,
	expire_on_commit=False,
)

async def get_async_db():
	async with AsyncSessionLocal() as db:
		try:
			yield db
		except Exception as e:
			await db.rollback()
			raise e
		finally:
			await db.close()
