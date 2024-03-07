import pytest
import uuid


def test_get_all_users(authorized_client):
    res = authorized_client.get(
        '/accounts',
    )
    assert res.status_code == 200


def test_get_user(authorized_client, test_user):
    user = test_user
    res = authorized_client.get(
        f'/accounts/{user["id"]}',
    )
    assert res.status_code == 200


def test_get_non_existing_user(authorized_client):
    res = authorized_client.get(
        f'/accounts/{uuid.uuid4()}',
    )
    assert res.status_code == 404


def test_update_user(authorized_client, test_user):
    user = {
        **test_user,
        'first_name': "first",
        "last_name": "last",
        "email": "updated@example.com",
        "is_admin": False,
        'divisions': []
    }
    res = authorized_client.put(
        f'/accounts/{user["id"]}',
        json=user
    )
    assert res.status_code == 200
    assert res.json()['first_name'] == "first"
    assert res.json()["last_name"] == "last"
    assert res.json()["email"] == "updated@example.com"
    assert res.json()["is_admin"] == False


def test_update_non_existing_user(authorized_client):
    user = {
        'first_name': "first",
        "last_name": "last",
        "email": "updated@example.com",
        'password': 'password',
        "is_admin": False,
        'divisions': []
    }
    res = authorized_client.put(
        f'/accounts/{uuid.uuid4()}',
        json=user
    )
    assert res.status_code == 404


def test_delete_user(authorized_client, test_user):
    user = test_user
    res = authorized_client.delete(
        f'/accounts/{user["id"]}',
    )
    assert res.status_code == 204


def test_delete_non_existing_user(authorized_client):
    res = authorized_client.delete(
        f'/accounts/{uuid.uuid4()}',
    )
    assert res.status_code == 404