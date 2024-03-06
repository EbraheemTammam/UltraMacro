import pytest


@pytest.fixture
def test_create_regulation(client):
    res = client.post(
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


def test_get_all_regulations(client):
    res = client.get(
        '/regulations',
    )
    assert res.status_code == 200


def test_get_regulation(client, test_create_regulation):
    regulation = test_create_regulation
    res = client.get(
        f'/regulations/{regulation["id"]}',
    )
    assert res.status_code == 200


def test_get_non_existing_regulation(client):
    res = client.get(
        '/regulations/1000',
    )
    assert res.status_code == 404


def test_update_regulation(client, test_create_regulation):
    regulation = {
        **test_create_regulation,
        'name': "updated regulation",
        'max_gpa': 4
    }
    res = client.put(
        f'/regulations/{regulation["id"]}',
        json=regulation
    )
    assert res.status_code == 200
    assert res.json()['name'] == "updated regulation"
    assert res.json()['max_gpa'] == 4


def test_update_non_existing_regulation(client):
    res = client.put(
        '/regulations/1000',
        json={
            'name': "updated regulation",
            'max_gpa': 4
        }
    )
    assert res.status_code == 404


def test_delete_regulation(client, test_create_regulation):
    regulation = test_create_regulation
    res = client.delete(
        f'/regulations/{regulation["id"]}',
    )
    assert res.status_code == 204


def test_delete_non_existing_regulation(client):
    res = client.delete(
        '/regulations/1000',
    )
    assert res.status_code == 404