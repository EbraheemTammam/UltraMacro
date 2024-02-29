import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from main import app
from authentication.oauth2 import create_access_token
from models import Base
from database.client import get_async_db


engine = create_engine(
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


@pytest.fixture(scope='function')
def client():
	Base.metadata.drop_all(bind=engine)
	Base.metadata.create_all(bind=engine)
	async def get_test_db():
		async with AsyncSessionLocal() as db:
			try:
				yield db
			except Exception as e:
				await db.rollback()
				raise e
			finally:
				await db.close()
	app.dependency_overrides[get_async_db] = get_test_db
	with TestClient(app) as client:
		yield client

@pytest.fixture
def test_user(client):
	user_data = {
	 'email': 'email@example.com',
	 'first_name': 'eepy',
	 'last_name': 'sleepy',
	 'password': 'password'
	}
	res = client.post(
	 'http://localhost:8000/users',
	 data=user_data
	)
	assert res.status_code == 201
	user = res.json()
	user['password'] = user_data['password']
	return user

@pytest.fixture
def token(test_user):
	return create_access_token({'user_id': test_user['id']})

@pytest.fixture
def authorized_client(client, token):
	client.headers = {
		**client.headers,
		'Authorization': f'Bearer {token}'
	}
	return client
