import pytest


@pytest.fixture
def test_create_course(authorized_client):
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
        }
    )
    assert res.status_code == 201
    assert res.json()["code"] == "TEST12"
    assert res.json()["name"] == "test course"
    assert res.json()["lecture_hours"] == 2
    assert res.json()["practical_hours"] == 1
    assert res.json()["credit_hours"] == 3
    assert res.json()["level"] == 1
    assert res.json()["semester"] == 1
    assert res.json()["required"] == True
    return res.json()


def test_get_all_courses(authorized_client):
    res = authorized_client.get(
        '/courses',
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


def test_update_course(authorized_client, test_create_course):
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
    }
    res = authorized_client.put(
        f'/courses/{course["id"]}',
        json=course
    )
    assert res.status_code == 200
    assert res.json()["code"] == "12TEST"
    assert res.json()["name"] == "updated course"
    assert res.json()["lecture_hours"] == 2
    assert res.json()["practical_hours"] == 0
    assert res.json()["credit_hours"] == 2
    assert res.json()["level"] == 2
    assert res.json()["semester"] == 2
    assert res.json()["required"] == False


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
    }
    res = authorized_client.put(
        '/courses/1000',
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