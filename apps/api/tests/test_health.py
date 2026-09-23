import pytest
from app.main import app
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_root_health():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "pragya-api"
    assert data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_api_v1_health():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "pragya-api"
    assert data["status"] == "ok"
    assert "database" in data
    assert data["database"]["connected"] is True
    assert data["database"]["dialect"] == "postgresql"
