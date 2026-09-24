import pytest
from backend.app.pipeline.ocr_engine import (
    clean_raw_plate,
    normalize_indian_plate,
    PlateTemporalAggregator
)

def test_clean_raw_plate():
    assert clean_raw_plate("mh-12 de 1433") == "MH12DE1433"
    assert clean_raw_plate("ga.07_ab-1234") == "GA07AB1234"
    assert clean_raw_plate("  DL  01 CA  9999 ") == "DL01CA9999"

def test_normalize_valid_indian_plate():
    plate, conf = normalize_indian_plate("MH12DE1433")
    assert plate == "MH12DE1433"
    assert conf >= 0.85

def test_normalize_character_substitutions():
    # 'O' in place of '0' in RTO code: MH O7 AB 1234 -> MH07AB1234
    plate, conf = normalize_indian_plate("MHO7AB1234")
    assert plate == "MH07AB1234"

    # '1' in place of 'I' in series letters: GA 07 1B 1234 -> GA07IB1234
    plate2, conf2 = normalize_indian_plate("GA071B1234")
    assert plate2 == "GA07IB1234"

def test_temporal_aggregator():
    agg = PlateTemporalAggregator(buffer_size=5)
    agg.add_observation(1, "MH12DE1433", 0.90)
    agg.add_observation(1, "MH12DE1433", 0.92)
    agg.add_observation(1, "MH12DE1438", 0.50) # noisy reading
    agg.add_observation(1, "MH12DE1433", 0.95)

    best_plate, avg_conf = agg.get_stable_plate(1)
    assert best_plate == "MH12DE1433"
    assert avg_conf > 0.80
