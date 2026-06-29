import pytest


VEHICLE_TYPES = ["car", "scooter", "bike", "pedestrian"]


@pytest.fixture
def vehicle_types():
    return VEHICLE_TYPES


@pytest.fixture
def sample_gps_position():
    return {
        "vehicle_id": "V00001",
        "type": "car",
        "status": "active",
        "timestamp": "2026-06-29T12:00:00+00:00",
        "lat": 48.8566,
        "lon": 2.3522,
        "altitude": 50.0,
        "speed": 35.0,
        "bearing": 180.0,
        "battery": 85.0,
    }


@pytest.fixture
def sample_vehicle():
    return {
        "id": "V00001",
        "type": "car",
        "status": "active",
        "lat": 48.8566,
        "lon": 2.3522,
        "speed": 35.0,
        "battery": 85.0,
    }
