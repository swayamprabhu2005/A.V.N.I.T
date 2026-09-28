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

def test_edge_telemetry_ingress():
    payload = {
        "camera_id": "ROAD-CAM-TEST-01",
        "location": "NH-48 Expressway KM 22",
        "plate_number": "MH12DE1433",
        "vehicle_type": "car",
        "observed_color": "white",
        "ocr_confidence": 0.98,
        "risk_score": 12.0,
        "risk_level": "GREEN",
        "reason": "Identity match confirmed",
        "is_night_mode": False
    }
    response = client.post("/api/telemetry/ingress", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "received"
    assert data["camera_id"] == "ROAD-CAM-TEST-01"
    assert "alert_id" in data

def test_edge_agent_script_download():
    response = client.get("/api/edge/agent-script")
    assert response.status_code == 200
    assert "Autonomous Roadside Edge Agent" in response.text

def test_edge_default_config_download():
    response = client.get("/api/edge/default-config")
    assert response.status_code == 200
    data = response.json()
    assert "camera_id" in data
    assert "server_url" in data

