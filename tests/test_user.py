import pytest
import uuid


def test_get_all_users(client):
    res = client.get(
        '/users',
    )
    assert res.status_code == 200


def test_get_user(client, test_user):
    user = test_user
    res = client.get(
        f'/users/{user["id"]}',
    )
    assert res.status_code == 200


def test_get_non_existing_user(client):
    res = client.get(
        f'/users/{uuid.uuid4()}',
    )
    assert res.status_code == 404


def test_update_user(client, test_user):
    user = {
        **test_user,
        'first_name': "first",
        "last_name": "last",
        "email": "updated@example.com",
        "is_admin": False
    }
    res = client.put(
        f'/users/{user["id"]}',
        json=user
    )
    assert res.status_code == 200
    assert res.json()['first_name'] == "first"
    assert res.json()["last_name"] == "last"
    assert res.json()["email"] == "updated@example.com"
    assert res.json()["is_admin"] == False


def test_update_non_existing_user(client):
    user = {
        'first_name': "first",
        "last_name": "last",
        "email": "updated@example.com",
        'password': 'password',
        "is_admin": False
    }
    res = client.put(
        f'/users/{uuid.uuid4()}',
        json=user
    )
    assert res.status_code == 404


def test_delete_user(client, test_user):
    user = test_user
    res = client.delete(
        f'/users/{user["id"]}',
    )
    assert res.status_code == 204
    res = client.delete(
        f'/users/{uuid.uuid4()}',
    )
    assert res.status_code == 404