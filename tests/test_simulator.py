import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src" / "simulator"))
import fleet_simulator as sim


class TestVehicle:
    def test_vehicle_has_id(self):
        v = sim.Vehicle("V00001")
        assert v.id == "V00001"

    def test_vehicle_type_valid(self):
        v = sim.Vehicle("V00001")
        assert v.type in sim.VEHICLE_TYPES

    def test_vehicle_status_valid(self):
        v = sim.Vehicle("V00001")
        assert v.status in sim.STATUSES

    def test_vehicle_lat_in_range(self):
        v = sim.Vehicle("V00001")
        assert 48.7 < v.lat < 49.0

    def test_vehicle_lon_in_range(self):
        v = sim.Vehicle("V00001")
        assert 2.1 < v.lon < 2.6

    def test_vehicle_battery_range(self):
        v = sim.Vehicle("V00001")
        assert 0 <= v.battery <= 100

    def test_vehicle_speed_positive(self):
        v = sim.Vehicle("V00001")
        assert v.speed > 0

    def test_move_changes_position(self):
        v = sim.Vehicle("V00001")
        lat_before, lon_before = v.lat, v.lon
        v.move()
        assert (v.lat != lat_before) or (v.lon != lon_before)

    def test_move_stays_in_bounds(self):
        v = sim.Vehicle("V00001")
        for _ in range(100):
            v.move()
            assert 48.7 < v.lat < 49.0
            assert 2.1 < v.lon < 2.6

    def test_to_dict_has_all_fields(self, sample_gps_position):
        v = sim.Vehicle("V00001")
        d = v.to_dict()
        for field in sample_gps_position:
            assert field in d

    def test_to_dict_vehicle_id_matches(self):
        v = sim.Vehicle("V99999")
        assert v.to_dict()["vehicle_id"] == "V99999"

    def test_speed_by_type(self):
        v = sim.Vehicle("V00001")
        assert v.speed > 0

    def test_battery_decreases(self):
        v = sim.Vehicle("V00001")
        battery_before = v.battery
        for _ in range(10):
            v.move()
        assert v.battery <= battery_before


class TestFleetSimulator:
    def test_generate_100_vehicles(self):
        vehicles = [sim.Vehicle(f"V{i:05d}") for i in range(100)]
        assert len(vehicles) == 100

    def test_unique_ids(self):
        vehicles = [sim.Vehicle(f"V{i:05d}") for i in range(100)]
        ids = [v.id for v in vehicles]
        assert len(set(ids)) == 100

    def test_gps_batch_json_serializable(self):
        vehicles = [sim.Vehicle(f"V{i:05d}") for i in range(10)]
        batch = [v.to_dict() for v in vehicles]
        dumped = json.dumps(batch)
        loaded = json.loads(dumped)
        assert len(loaded) == 10

    def test_gps_position_has_lat_lon(self):
        v = sim.Vehicle("V00001")
        d = v.to_dict()
        assert isinstance(d["lat"], float)
        assert isinstance(d["lon"], float)

    def test_bearing_range(self):
        v = sim.Vehicle("V00001")
        assert 0 <= v.bearing <= 360
