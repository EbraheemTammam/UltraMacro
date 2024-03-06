from uuid import uuid4
import pytest

from .test_regulation import test_create_regulation
from .test_department import test_create_department
from .test_division import test_create_division

@pytest.fixture
def test_create_student(client, test_create_division):
    group = test_create_division
    res = client.post(
        '/students',
        json={
            "name": "test student",
            "group_id": group["id"],
            "division_id": None,
        }
    )
    assert res.status_code == 201
    assert res.json()["name"] == "test student"
    assert res.json()["group"]["id"] == group["id"]
    assert res.json()["division"] == None
    assert res.json()["registered_hours"] == 0
    assert res.json()["passed_hours"] == 0
    assert res.json()["excluded_hours"] == 0
    assert res.json()["research_hours"] == 0
    assert res.json()["gpa"] == 0
    assert res.json()["total_mark"] == 0
    assert res.json()["level"] == 1
    assert res.json()["graduate"] == False
    return res.json()


def test_get_all_students(client):
    res = client.get(
        '/students',
    )
    assert res.status_code == 200


def test_get_student(client, test_create_student):
    student = test_create_student
    res = client.get(
        f'/students/{student["id"]}',
    )
    assert res.status_code == 200


def test_get_non_existing_student(client):
    res = client.get(
        f'/students/{uuid4()}',
    )
    assert res.status_code == 404


def test_update_student(client, test_create_student, test_create_division):
    group = test_create_division
    division = test_create_division
    student = {
        **test_create_student,
        "name": "updated student",
        "group_id": group["id"],
        "division_id": division["id"],
    }
    res = client.put(
        f'/students/{student["id"]}',
        json=student
    )
    assert res.status_code == 200
    assert res.json()["name"] == "updated student"
    assert res.json()["group"]["id"] == group["id"]
    assert res.json()["division"]["id"] == division["id"]
    assert res.json()["registered_hours"] == 0
    assert res.json()["passed_hours"] == 0
    assert res.json()["excluded_hours"] == 0
    assert res.json()["research_hours"] == 0
    assert res.json()["gpa"] == 0
    assert res.json()["total_mark"] == 0
    assert res.json()["level"] == 1
    assert res.json()["graduate"] == False


def test_update_non_exisitng_student(client, test_create_student, test_create_division):
    group = test_create_division
    division = test_create_division
    student = {
        **test_create_student,
        "name": "updated student",
        "group_id": group["id"],
        "division_id": division["id"],
    }
    res = client.put(
        f'/students/{uuid4()}',
        json=student
    )
    assert res.status_code == 404


def test_delete_student(client, test_create_student):
    student = test_create_student
    res = client.delete(
        f'/students/{student["id"]}',
    )
    assert res.status_code == 204


def test_delete_non_exisitng_student(client):
    res = client.delete(
        f'/students/{uuid4()}',
    )
    assert res.status_code == 404