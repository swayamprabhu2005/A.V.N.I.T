import pytest
from backend.app.database import (
    init_db,
    add_vehicle,
    get_vehicle_by_plate,
    update_vehicle,
    delete_vehicle,
    list_vehicles,
    log_event,
    list_alerts,
    get_stats
)

def test_database_crud():
    init_db()
    test_plate = "MH99CR1234"
    
    # 1. Add
    v_id = add_vehicle(
        plate_number=test_plate,
        vehicle_type="car",
        color="red",
        make="Toyota",
        model="Corolla"
    )
    assert v_id > 0

    # 2. Get
    v = get_vehicle_by_plate(test_plate)
    assert v is not None
    assert v["plate_number"] == test_plate
    assert v["color"] == "red"

    # 3. Update
    updated = update_vehicle(
        vehicle_id=v["vehicle_id"],
        plate_number=test_plate,
        vehicle_type="car",
        color="black",
        make="Toyota",
        model="Corolla",
        registration_status="Active"
    )
    assert updated is True
    v_after = get_vehicle_by_plate(test_plate)
    assert v_after["color"] == "black"

    # 4. Log Alert
    alert_id = log_event(
        track_id=10,
        plate_number=test_plate,
        ocr_confidence=0.90,
        observed_type="car",
        observed_color="black",
        risk_score=15.0,
        risk_level="GREEN",
        reason="Match verified"
    )
    assert alert_id > 0

    # 5. List alerts & stats
    alerts = list_alerts(limit=5)
    assert len(alerts) > 0
    stats = get_stats()
    assert stats["registered_vehicles"] > 0

    # 6. Delete
    deleted = delete_vehicle(v["vehicle_id"])
    assert deleted is True
    assert get_vehicle_by_plate(test_plate) is None
