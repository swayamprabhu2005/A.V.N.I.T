import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_system_status():
    response = client.get("/api/system/status")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert data["status"] == "online"

def test_get_vehicles():
    response = client.get("/api/vehicles")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_stats():
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "registered_vehicles" in data
    assert "total_detections" in data
