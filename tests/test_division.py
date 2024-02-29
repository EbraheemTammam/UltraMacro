import pytest

from .test_regulation import test_create_regulation
from .test_department import test_create_department


@pytest.fixture
def test_create_division(client, test_create_regulation, test_create_department):
    regulation = test_create_regulation
    department_1 = test_create_department
    department_2 = test_create_department
    res = client.post(
        '/divisions',
        json={
            "name": "test division",
            "hours": 142,
            "private": False,
            "group": False,
            "regulation_id": regulation["id"],
            "department_1_id": department_1["id"],
            "department_2_id": department_2["id"]
        }
    )
    assert res.status_code == 201
    assert res.json()["name"] == "test division"
    assert res.json()["hours"] == 142
    assert res.json()["private"] == False
    assert res.json()["group"] == False
    assert res.json()["regulation"]["id"] == regulation["id"]
    assert res.json()["department_1"]["id"] == department_1["id"]
    assert res.json()["department_2"]["id"] == department_2["id"]
    return res.json()


def test_get_all_divisions(client):
    res = client.get(
        '/divisions',
    )
    assert res.status_code == 200


def test_get_division(client, test_create_division):
    division = test_create_division
    res = client.get(
        f'/divisions/{division["id"]}',
    )
    assert res.status_code == 200
    res = client.get(
        '/divisions/1000',
    )
    assert res.status_code == 404


def test_update_division(client, test_create_division, test_create_regulation, test_create_department):
    regulation = test_create_regulation
    department_1 = test_create_department
    department_2 = test_create_department
    division = test_create_division
    division['name'] = "updated division"
    division["hours"] = 142
    division["private"] = False
    division["group"] = False
    division["regulation_id"] = regulation["id"]
    division["department_1_id"] = department_1["id"]
    division["department_2_id"] = department_2["id"]
    res = client.put(
        f'/divisions/{division["id"]}',
        json=division
    )
    assert res.status_code == 200
    assert res.json()['name'] == "updated division"
    assert res.json()["hours"] == 142
    assert res.json()["private"] == False
    assert res.json()["group"] == False
    assert res.json()["regulation"]["id"] == regulation["id"]
    assert res.json()["department_1"]["id"] == department_1["id"]
    assert res.json()["department_2"]["id"] == department_2["id"]
    res = client.put(
        '/divisions/1000',
        json=division
    )
    assert res.status_code == 404


def test_delete_division(client, test_create_division):
    division = test_create_division
    res = client.delete(
        f'/divisions/{division["id"]}',
    )
    assert res.status_code == 204
    res = client.delete(
        '/divisions/1000',
    )
    assert res.status_code == 404