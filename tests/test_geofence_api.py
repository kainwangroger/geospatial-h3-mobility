from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src" / "api"))
from geofence_api import haversine, GEOFENCE_ZONES, app

from fastapi.testclient import TestClient

client = TestClient(app)


class TestHaversine:
    def test_zero_distance(self):
        d = haversine(48.8566, 2.3522, 48.8566, 2.3522)
        assert d == 0.0

    def test_paris_to_london(self):
        d = haversine(48.8566, 2.3522, 51.5074, -0.1278)
        assert 300 < d < 400

    def test_paris_to_ny(self):
        d = haversine(48.8566, 2.3522, 40.7128, -74.0060)
        assert 5500 < d < 6000


class TestAPIHealth:
    def test_health_returns_ok(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    def test_health_zones_loaded(self):
        resp = client.get("/health")
        assert resp.json()["zones_loaded"] == len(GEOFENCE_ZONES)


class TestAPIZones:
    def test_list_zones(self):
        resp = client.get("/geofence/zones")
        assert resp.status_code == 200
        assert "zones" in resp.json()

    def test_all_zones_listed(self):
        resp = client.get("/geofence/zones")
        zones = resp.json()["zones"]
        for name in GEOFENCE_ZONES:
            assert name in zones


class TestGeofenceCheck:
    def test_point_inside_zone(self):
        resp = client.post("/geofence/check", json={
            "point": {"lat": 48.8566, "lon": 2.3522},
            "zone_name": "paris_centre",
        })
        assert resp.status_code == 200
        assert resp.json()["inside"] is True

    def test_point_outside_zone(self):
        resp = client.post("/geofence/check", json={
            "point": {"lat": 49.0097, "lon": 2.5479},
            "zone_name": "paris_centre",
        })
        assert resp.status_code == 200
        assert resp.json()["inside"] is False

    def test_unknown_zone(self):
        resp = client.post("/geofence/check", json={
            "point": {"lat": 48.8566, "lon": 2.3522},
            "zone_name": "unknown_zone",
        })
        assert resp.status_code == 404


class TestETA:
    def test_eta_returns_distance(self):
        resp = client.post("/eta", json={
            "origin": {"lat": 48.8566, "lon": 2.3522},
            "destination": {"lat": 48.8917, "lon": 2.2389},
            "vehicle_type": "car",
        })
        assert resp.status_code == 200
        assert resp.json()["distance_km"] > 0

    def test_eta_duration_positive(self):
        resp = client.post("/eta", json={
            "origin": {"lat": 48.8566, "lon": 2.3522},
            "destination": {"lat": 48.8917, "lon": 2.2389},
            "vehicle_type": "pedestrian",
        })
        assert resp.json()["duration_min"] > 0

    def test_eta_car_faster_than_pedestrian(self):
        car = client.post("/eta", json={
            "origin": {"lat": 48.8566, "lon": 2.3522},
            "destination": {"lat": 48.8917, "lon": 2.2389},
            "vehicle_type": "car",
        }).json()
        ped = client.post("/eta", json={
            "origin": {"lat": 48.8566, "lon": 2.3522},
            "destination": {"lat": 48.8917, "lon": 2.2389},
            "vehicle_type": "pedestrian",
        }).json()
        assert car["duration_min"] < ped["duration_min"]

    def test_eta_same_point(self):
        resp = client.post("/eta", json={
            "origin": {"lat": 48.8566, "lon": 2.3522},
            "destination": {"lat": 48.8566, "lon": 2.3522},
            "vehicle_type": "car",
        })
        assert resp.json()["distance_km"] == 0
        assert resp.json()["duration_min"] == 0

    def test_eta_invalid_vehicle_defaults(self):
        resp = client.post("/eta", json={
            "origin": {"lat": 48.8566, "lon": 2.3522},
            "destination": {"lat": 48.8917, "lon": 2.2389},
            "vehicle_type": "rocket",
        })
        assert resp.status_code == 200
        assert resp.json()["duration_min"] > 0
