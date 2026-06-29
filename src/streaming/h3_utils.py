"""
Utilitaires H3 pour l'indexation hexagonale.

Utilise la bibliothèque h3-py quand disponible,
avec une émulation simple en fallback pour les tests.
"""

import math


def lat_lon_to_h3(lat, lon, resolution=9):
    try:
        import h3
        return h3.latlng_to_cell(lat, lon, resolution)
    except ImportError:
        return _h3_fallback(lat, lon, resolution)


def h3_to_center(h3_index):
    try:
        import h3
        return h3.cell_to_latlng(h3_index)
    except ImportError:
        parts = h3_index.split("x")
        lat = float(parts[-2]) if len(parts) > 1 else 0.0
        lon = float(parts[-1]) if len(parts) > 1 else 0.0
        return lat, lon


def h3_to_boundary(h3_index):
    try:
        import h3
        return h3.cell_to_boundary(h3_index)
    except ImportError:
        lat, lon = h3_to_center(h3_index)
        return [(lat + 0.001, lon + 0.001), (lat - 0.001, lon + 0.001),
                (lat - 0.001, lon - 0.001), (lat + 0.001, lon - 0.001)]


def k_ring(h3_index, k=1):
    try:
        import h3
        return h3.grid_disk(h3_index, k)
    except ImportError:
        return [h3_index]


def _h3_fallback(lat, lon, resolution=9):
    r = resolution
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    lat_int = int((lat_rad * 1000000) // (r + 1))
    lon_int = int((lon_rad * 1000000) // (r + 1))
    return f"h3_r{r}x{lat_int}x{lon_int}"


VALID_RESOLUTIONS = list(range(0, 16))


def is_valid_resolution(r):
    return 0 <= r <= 15
