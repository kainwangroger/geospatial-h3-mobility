from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src" / "streaming"))
import h3_utils


class TestH3Utils:
    def test_lat_lon_to_h3_returns_string(self):
        h3 = h3_utils.lat_lon_to_h3(48.8566, 2.3522)
        assert isinstance(h3, str)
        assert len(h3) > 0

    def test_h3_fallback_format(self):
        h3 = h3_utils._h3_fallback(48.8566, 2.3522, 9)
        assert h3.startswith("h3_r9x")

    def test_h3_different_locations(self):
        h3_1 = h3_utils.lat_lon_to_h3(48.8566, 2.3522)
        h3_2 = h3_utils.lat_lon_to_h3(48.8066, 2.4022)
        assert h3_1 != h3_2

    def test_h3_same_location(self):
        h3_1 = h3_utils.lat_lon_to_h3(48.8566, 2.3522)
        h3_2 = h3_utils.lat_lon_to_h3(48.8566, 2.3522)
        assert h3_1 == h3_2

    def test_h3_to_center_returns_tuple(self):
        h3 = h3_utils.lat_lon_to_h3(48.8566, 2.3522)
        center = h3_utils.h3_to_center(h3)
        assert isinstance(center, tuple)
        assert len(center) == 2

    def test_different_resolutions(self):
        h3_low = h3_utils.lat_lon_to_h3(48.8566, 2.3522, 8)
        h3_high = h3_utils.lat_lon_to_h3(48.8566, 2.3522, 12)
        assert h3_low != h3_high

    def test_k_ring_returns_list(self):
        h3 = h3_utils.lat_lon_to_h3(48.8566, 2.3522)
        ring = h3_utils.k_ring(h3, 1)
        assert isinstance(ring, list)
        assert len(ring) >= 1

    def test_k_ring_includes_center(self):
        h3 = h3_utils.lat_lon_to_h3(48.8566, 2.3522)
        ring = h3_utils.k_ring(h3, 0)
        assert h3 in ring

    def test_valid_resolutions(self):
        for r in h3_utils.VALID_RESOLUTIONS:
            assert h3_utils.is_valid_resolution(r)

    def test_invalid_resolutions(self):
        assert not h3_utils.is_valid_resolution(-1)
        assert not h3_utils.is_valid_resolution(16)

    def test_h3_to_boundary_returns_list(self):
        h3 = h3_utils.lat_lon_to_h3(48.8566, 2.3522)
        boundary = h3_utils.h3_to_boundary(h3)
        assert isinstance(boundary, list)
        assert len(boundary) >= 3
