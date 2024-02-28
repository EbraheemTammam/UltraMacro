import pytest


@pytest.mark.asyncio
@pytest.fixture
async def test_create_regulation(client):
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


@pytest.mark.asyncio
async def test_get_all_regulations(client):
    res = client.get(
        '/regulations',
    )
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_get_regulation(client, test_create_regulation):
    regulation = await test_create_regulation
    res = client.get(
        f'/regulations/{regulation["id"]}',
    )
    assert res.status_code == 200
    res = client.get(
        '/regulations/1000',
    )
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_update_regulation(client, test_create_regulation):
    regulation = await test_create_regulation
    regulation['name'] = "updated regulation"
    regulation['max_gpa'] = 4
    res = client.put(
        f'/regulations/{regulation["id"]}',
        json=regulation
    )
    assert res.status_code == 200
    assert res.json()['name'] == "updated regulation"
    assert res.json()['max_gpa'] == 4
    res = client.put(
        '/regulations/1000',
        json=regulation
    )
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_delete_regulation(client, test_create_regulation):
    regulation = await test_create_regulation
    res = client.delete(
        f'/regulations/{regulation["id"]}',
    )
    assert res.status_code == 204
    res = client.delete(
        '/regulations/1000',
    )
    assert res.status_code == 404