import asyncio
import os
import pytest
from httpx import AsyncClient
from testcontainers.mongodb import MongoDbContainer
from testcontainers.redis import RedisContainer

from app import app

@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop

@pytest.fixture(scope="module")
async def test_env():
    with MongoDbContainer() as mongodb, RedisContainer() as redis:
        os.environ["MONGO_URI"] = mongodb.get_connection_url()
        os.environ["REDIS_URL"] = f"redis://{redis.get_container_host_ip()}:{redis.get_exposed_port(6379)}/0"
        yield

@pytest.mark.asyncio
async def test_register_login_refresh(test_env):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # register
        r = await ac.post("/api/v1/auth/register", json={"email": "test@example.com", "password": "password123"})
        assert r.status_code == 200
        # login
        r = await ac.post("/api/v1/auth/token", data={"username": "test@example.com", "password": "password123"})
        assert r.status_code == 200
        tokens = r.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        # get me
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        r = await ac.get("/api/v1/users/me", headers=headers)
        assert r.status_code == 200