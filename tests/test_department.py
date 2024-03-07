import pytest


@pytest.fixture
def test_create_department(authorized_client):
    res = authorized_client.post(
        '/departments',
        json={
            "name": "test department",
        }
    )
    assert res.status_code == 201
    assert res.json()["name"] == "test department"
    return res.json()


def test_get_all_departments(authorized_client):
    res = authorized_client.get(
        '/departments',
    )
    assert res.status_code == 200


def test_get_department(authorized_client, test_create_department):
    department = test_create_department
    res = authorized_client.get(
        f'/departments/{department["id"]}',
    )
    assert res.status_code == 200


def test_get_non_existing_department(authorized_client):
    res = authorized_client.get(
        '/departments/1000',
    )
    assert res.status_code == 404


def test_update_department(authorized_client, test_create_department):
    department = test_create_department
    department['name'] = "updated department"
    res = authorized_client.put(
        f'/departments/{department["id"]}',
        json=department
    )
    assert res.status_code == 200
    assert res.json()['name'] == "updated department"


def test_update_non_existing_department(authorized_client):
    res = authorized_client.put(
        '/departments/1000',
        json={'name': 'updated'}
    )
    assert res.status_code == 404


def test_delete_department(authorized_client, test_create_department):
    department = test_create_department
    res = authorized_client.delete(
        f'/departments/{department["id"]}',
    )
    assert res.status_code == 204


def test_delete_non_existing_department(authorized_client):
    res = authorized_client.delete(
        '/departments/1000',
    )
    assert res.status_code == 404