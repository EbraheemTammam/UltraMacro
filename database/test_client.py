from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession


test_engine = create_engine(
	'sqlite:///test_db.sqlite3',
	connect_args={'check_same_thread': False}, # uncomment if using sqlite
)

async_engine = create_async_engine(
	'sqlite+aiosqlite:///test_db.sqlite3',
	connect_args={'check_same_thread': False}, # uncomment if using sqlite
)

AsyncSessionLocal = sessionmaker(
	async_engine,
	autocommit=False,
	autoflush=False,
	class_=AsyncSession,
	expire_on_commit=False,
)

async def get_test_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db
        except Exception as e:
            await db.rollback()
            raise e
        finally:
            await db.close()