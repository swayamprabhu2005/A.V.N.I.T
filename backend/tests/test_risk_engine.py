import pytest
from backend.app.database import init_db, add_vehicle, delete_vehicle, get_vehicle_by_plate
from backend.app.pipeline.risk_engine import evaluate_identity_risk

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    init_db()
    # Add known test vehicle
    add_vehicle(
        plate_number="TEST01AB1111",
        vehicle_type="car",
        color="white",
        make="Hyundai",
        model="i20"
    )
    yield
    v = get_vehicle_by_plate("TEST01AB1111")
    if v:
        delete_vehicle(v["vehicle_id"])

def test_valid_vehicle_matching():
    # Observed white car matching registered white car
    res = evaluate_identity_risk(
        plate_number="TEST01AB1111",
        ocr_confidence=0.95,
        observed_type="car",
        observed_color="white",
        observed_make="Hyundai",
        observed_model="i20"
    )
    assert res["risk_level"] == "GREEN"
    assert res["risk_score"] < 25.0
    assert res["is_tampered"] is False

def test_vehicle_type_mismatch():
    # Observed motorcycle displaying registered car plate
    res = evaluate_identity_risk(
        plate_number="TEST01AB1111",
        ocr_confidence=0.90,
        observed_type="motorcycle",
        observed_color="white"
    )
    assert res["risk_level"] in ["YELLOW", "RED"]
    assert "Vehicle Type Mismatch" in res["reason"]

def test_vehicle_color_mismatch():
    # Observed black car displaying registered white car plate
    res = evaluate_identity_risk(
        plate_number="TEST01AB1111",
        ocr_confidence=0.90,
        observed_type="car",
        observed_color="black"
    )
    assert "Color Mismatch" in res["reason"]

def test_unregistered_plate_alert():
    # Unknown / unregistered plate
    res = evaluate_identity_risk(
        plate_number="UNKNOWN9999",
        ocr_confidence=0.92,
        observed_type="car",
        observed_color="blue"
    )
    assert res["risk_level"] == "RED"
    assert res["registered"] is False
    assert res["is_tampered"] is True
    assert "Unregistered Plate Alert" in res["reason"]
