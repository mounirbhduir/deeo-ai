"""
Tests pour endpoint health check
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    """Test endpoint /api/health"""
    response = await client.get("/api/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert "api" in data
    assert data["api"] == "ok"


@pytest.mark.asyncio
async def test_version_endpoint(client: AsyncClient):
    """Test endpoint /api/version"""
    response = await client.get("/api/version")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "version" in data
    assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test endpoint racine /"""
    response = await client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "message" in data
    assert "version" in data
    assert "docs" in data