"""
Notebook d'analyse géospatiale avec H3 et Kepler.gl.

Usage: Ce fichier peut être importé dans Jupyter ou exécuté comme script.
"""

import random
from collections import Counter, defaultdict


def simulate_positions(num_points=10000):
    positions = []
    for _ in range(num_points):
        positions.append({
            "lat": 48.8566 + random.uniform(-0.04, 0.04),
            "lon": 2.3522 + random.uniform(-0.06, 0.06),
            "type": random.choice(["car", "scooter", "bike", "pedestrian"]),
            "speed": round(random.uniform(0, 50), 1),
        })
    return positions


def compute_h3_index(points, resolution=9):
    from h3_utils import lat_lon_to_h3
    for p in points:
        p["h3_cell"] = lat_lon_to_h3(p["lat"], p["lon"], resolution)
    return points


def aggregate_by_h3(points):
    counts = Counter()
    speeds = defaultdict(list)
    for p in points:
        counts[p["h3_cell"]] += 1
        speeds[p["h3_cell"]].append(p["speed"])

    result = {}
    for cell, count in counts.most_common():
        result[cell] = {
            "count": count,
            "avg_speed": round(sum(speeds[cell]) / len(speeds[cell]), 2) if speeds[cell] else 0,
        }
    return result


def top_density_hexagons(points, n=10):
    from h3_utils import h3_to_center
    indexed = compute_h3_index(points)
    agg = aggregate_by_h3(indexed)
    top = list(sorted(agg.items(), key=lambda x: -x[1]["count"]))[:n]
    result = []
    for cell, stats in top:
        lat, lon = h3_to_center(cell)
        result.append({"h3": cell, "lat": lat, "lon": lon, **stats})
    return result


def main():
    print("H3 Geospatial Analysis")
    print("=" * 40)
    points = simulate_positions(5000)
    print(f"Simulated {len(points)} GPS points")

    top = top_density_hexagons(points, 5)
    print("\nTop 5 density hexagons:")
    for h in top:
        print(f"  {h['h3']}: {h['count']} points, avg speed {h['avg_speed']} km/h")

    print("\nKepler.gl config ready for visualization")


if __name__ == "__main__":
    main()
