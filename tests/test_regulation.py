import pytest


@pytest.fixture
def test_create_regulation(authorized_client):
    res = authorized_client.post(
        '/regulations',
        json={
            "name": "test regulation",
            "max_gpa": 5
        }
    )
    assert res.status_code == 201
    assert res.json()["name"] == "test regulation"
    assert res.json()["max_gpa"] == 5
    return res.json()


def test_get_all_regulations(authorized_client):
    res = authorized_client.get(
        '/regulations',
    )
    assert res.status_code == 200


def test_get_regulation(authorized_client, test_create_regulation):
    regulation = test_create_regulation
    res = authorized_client.get(
        f'/regulations/{regulation["id"]}',
    )
    assert res.status_code == 200


def test_get_non_existing_regulation(authorized_client):
    res = authorized_client.get(
        '/regulations/-1',
    )
    assert res.status_code == 404


def test_update_regulation(authorized_client, test_create_regulation):
    regulation = {
        **test_create_regulation,
        'name': "updated regulation",
        'max_gpa': 4
    }
    res = authorized_client.put(
        f'/regulations/{regulation["id"]}',
        json=regulation
    )
    assert res.status_code == 200
    assert res.json()['name'] == "updated regulation"
    assert res.json()['max_gpa'] == 4


def test_update_non_existing_regulation(authorized_client):
    res = authorized_client.put(
        '/regulations/-1',
        json={
            'name': "updated regulation",
            'max_gpa': 4
        }
    )
    assert res.status_code == 404


def test_delete_regulation(authorized_client, test_create_regulation):
    regulation = test_create_regulation
    res = authorized_client.delete(
        f'/regulations/{regulation["id"]}',
    )
    assert res.status_code == 204


def test_delete_non_existing_regulation(authorized_client):
    res = authorized_client.delete(
        '/regulations/-1',
    )
    assert res.status_code == 404