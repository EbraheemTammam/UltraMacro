import pytest

from .test_regulation import test_create_regulation
from .test_department import test_create_department
from .test_division import test_create_division


@pytest.fixture
def test_create_course(authorized_client, test_create_division):
    division = test_create_division
    res = authorized_client.post(
        '/courses',
        json={
            "code": "TEST12",
            "name": "test course",
            "lecture_hours": 2,
            "practical_hours": 1,
            "credit_hours": 3,
            "level": 1,
            "semester": 1,
            "required": True,
            "divisions": [division['id']]
        }
    )
    assert res.status_code == 201
    res = res.json()
    assert res["code"] == "TEST12"
    assert res["name"] == "test course"
    assert res["lecture_hours"] == 2
    assert res["practical_hours"] == 1
    assert res["credit_hours"] == 3
    assert res["level"] == 1
    assert res["semester"] == 1
    assert res["required"] == True
    assert res["divisions"][0]["id"] == division["id"]
    return res


def test_get_all_courses(authorized_client, test_create_regulation):
    regulation = test_create_regulation
    res = authorized_client.get(
        f'/courses?regulation={regulation["id"]}',
    )
    assert res.status_code == 200


def test_get_course(authorized_client, test_create_course):
    course = test_create_course
    res = authorized_client.get(
        f'/courses/{course["id"]}',
    )
    assert res.status_code == 200


def test_get_non_existing_course(authorized_client):
    res = authorized_client.get(
        '/courses/1000',
    )
    assert res.status_code == 404


def test_update_course(authorized_client, test_create_course, test_create_division):
    division = test_create_division
    course = {
        **test_create_course,
        "code": "12TEST",
        "name": "updated course",
        "lecture_hours": 2,
        "practical_hours": 0,
        "credit_hours": 2,
        "level": 2,
        "semester": 2,
        "required": False,
        "divisions": [division["id"]]
    }
    res = authorized_client.put(
        f'/courses/{course["id"]}',
        json=course
    )
    assert res.status_code == 200
    res = res.json()
    assert res["code"] == "12TEST"
    assert res["name"] == "updated course"
    assert res["lecture_hours"] == 2
    assert res["practical_hours"] == 0
    assert res["credit_hours"] == 2
    assert res["level"] == 2
    assert res["semester"] == 2
    assert res["required"] == False
    assert res["divisions"][0]["id"] == division["id"]


def test_update_non_exisitng_course(authorized_client):
    course = {
        "code": "12TEST",
        "name": "updated course",
        "lecture_hours": 2,
        "practical_hours": 0,
        "credit_hours": 2,
        "level": 2,
        "semester": 2,
        "required": False,
        "divisions": []
    }
    res = authorized_client.put(
        '/courses/-1',
        json=course
    )
    assert res.status_code == 404


def test_delete_course(authorized_client, test_create_course):
    course = test_create_course
    res = authorized_client.delete(
        f'/courses/{course["id"]}',
    )
    assert res.status_code == 204


def test_delete_non_exisitng_course(authorized_client):
    res = authorized_client.delete(
        '/courses/1000',
    )
    assert res.status_code == 404