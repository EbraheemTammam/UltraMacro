import pytest


@pytest.mark.asyncio
@pytest.fixture
async def test_create_department(client):
    res = client.post(
        '/departments',
        json={
            "name": "test department",
        }
    )
    assert res.status_code == 201
    assert res.json()["name"] == "test department"
    return res.json()


@pytest.mark.asyncio
async def test_get_all_departments(client):
    res = client.get(
        '/departments',
    )
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_get_department(client, test_create_department):
    department = await test_create_department
    res = client.get(
        f'/departments/{department["id"]}',
    )
    assert res.status_code == 200
    res = client.get(
        '/departments/1000',
    )
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_update_department(client, test_create_department):
    department = await test_create_department
    department['name'] = "updated department"
    res = client.put(
        f'/departments/{department["id"]}',
        json=department
    )
    assert res.status_code == 200
    assert res.json()['name'] == "updated department"
    res = client.put(
        '/departments/1000',
        json=department
    )
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_delete_department(client, test_create_department):
    department = await test_create_department
    res = client.delete(
        f'/departments/{department["id"]}',
    )
    assert res.status_code == 204
    res = client.delete(
        '/departments/1000',
    )
    assert res.status_code == 404