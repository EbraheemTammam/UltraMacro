import pytest
from fastapi.testclient import TestClient


from main import app
from authentication.oauth2 import create_access_token
from config import Base
from database import test_engine, get_test_db, get_async_db


@pytest.fixture(scope='function')
def client():
	Base.metadata.drop_all(bind=test_engine)
	Base.metadata.create_all(bind=test_engine)
	
	app.dependency_overrides[get_async_db] = get_test_db
	with TestClient(app) as client:
		yield client

@pytest.fixture(scope='function')
def test_user(client):
	user_data = {
		'email': 'email@example.com',
		'first_name': 'eepy',
		'last_name': 'sleepy',
		'password': 'password',
		'is_admin': True,
		'divisions': []
	}
	res = client.post(
		'http://localhost:8000/accounts',
		json=user_data
	)
	assert res.status_code == 201
	user = res.json()
	user['password'] = user_data['password']
	return user

@pytest.fixture
def token(test_user):
	return create_access_token({'user_id': test_user['id'], 'is_admin': True})

@pytest.fixture
def authorized_client(client, token):
	client.headers = {
		**client.headers,
		'Authorization': f'Bearer {token}'
	}
	return client
