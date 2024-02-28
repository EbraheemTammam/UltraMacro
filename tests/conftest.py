import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from authentication.oath2 import create_access_token
from models import Base
from database.client import get_db
from config import settings


engine = create_engine(
	settings.DATABASE_URL + '_test',
# connect_args={check_same_thread: False} # uncomment if using sqlite
)

SessionLocal = sessionmaker(
	autocommit=False,
	autoflush=False,
	bind=engine
)

@pytest.fixture(scope='function')
def session():
	db = SessionLocal()
	Base.metadata.drop_all(bind=engine)
	Base.metadata.create_all(bind=engine)
	try:
		yield db
	finally:
		db.close()

@pytest.fixture(scope='function')
def client(session):
	def get_test_db():
		try:
			yield session
		finally:
			session.close()
	app.dependency_overrides[get_db] = get_test_db
	yield TestClient(app)

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
