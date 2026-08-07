"""
Базовый smoke-тест. Полные unit/integration тесты для auth и project
сервисов (с тестовой БД через testcontainers) добавляются вместе
с CI-пайплайном в главе 20 (Testing & QA Framework).
"""
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_check() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
