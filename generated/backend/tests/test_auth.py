import pytest
from httpx import AsyncClient
from app import app

@pytest.mark.asyncio
async def test_register_login_refresh(monkeypatch):
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register
        r = await client.post("/api/v1/auth/register", json={"email": "alice@example.com", "password": "password123", "full_name": "Alice"})
        assert r.status_code == 200
        data = r.json()
        assert "user_id" in data

        # Login
        r = await client.post("/api/v1/auth/login", json={"email": "alice@example.com", "password": "password123"})
        assert r.status_code == 200
        tokens = r.json()
        assert "access_token" in tokens and "refresh_token" in tokens

        # Refresh
        r = await client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
        assert r.status_code == 200
        data = r.json()
        assert "access_token" in data and "refresh_token" in data