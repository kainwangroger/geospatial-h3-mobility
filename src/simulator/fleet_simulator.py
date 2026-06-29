"""
Simulateur de flotte de véhicules GPS.

1000 véhicules émettent leur position toutes les 5 secondes.
Types : voiture, scooter, vélo, piéton.

Usage: python fleet_simulator.py [num_vehicles] [interval_sec]
"""

import json
import math
import random
import subprocess
import sys
import time
from datetime import datetime, timezone

VEHICLE_TYPES = ["car", "scooter", "bike", "pedestrian"]
STATUSES = ["active", "idle", "offline"]
COLORS = ["red", "blue", "green", "yellow", "white", "black", "silver"]

# Paris approximate bounding box
LAT_CENTER = 48.8566
LON_CENTER = 2.3522
LAT_SPAN = 0.08
LON_SPAN = 0.12


class Vehicle:
    def __init__(self, vehicle_id):
        self.id = vehicle_id
        self.type = random.choice(VEHICLE_TYPES)
        self.status = "active"
        self.color = random.choice(COLORS)
        self.speed = {"car": random.uniform(20, 50), "scooter": random.uniform(10, 25),
                      "bike": random.uniform(8, 18), "pedestrian": random.uniform(3, 6)}[self.type]
        self.lat = LAT_CENTER + random.uniform(-LAT_SPAN / 2, LAT_SPAN / 2)
        self.lon = LON_CENTER + random.uniform(-LON_SPAN / 2, LON_SPAN / 2)
        self.heading = random.uniform(0, 360)
        self.bearing = random.uniform(0, 360)
        self.altitude = random.uniform(30, 120)
        self.battery = random.uniform(20, 100)

    def move(self):
        self.bearing += random.uniform(-15, 15)
        speed_ms = self.speed * 1000 / 3600
        self.lat += speed_ms * math.cos(math.radians(self.bearing)) / 111320 * 5
        self.lon += speed_ms * math.sin(math.radians(self.bearing)) / (111320 * math.cos(math.radians(self.lat))) * 5

        self.lat = max(LAT_CENTER - LAT_SPAN / 2, min(LAT_CENTER + LAT_SPAN / 2, self.lat))
        self.lon = max(LON_CENTER - LON_SPAN / 2, min(LON_CENTER + LON_SPAN / 2, self.lon))

        if random.random() < 0.01:
            self.status = random.choice(STATUSES)
        self.battery = max(0, self.battery - random.uniform(0, 0.5))

    def to_dict(self):
        return {
            "vehicle_id": self.id,
            "type": self.type,
            "status": self.status,
            "color": self.color,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "lat": round(self.lat, 6),
            "lon": round(self.lon, 6),
            "altitude": round(self.altitude, 1),
            "speed": round(self.speed, 1),
            "bearing": round(self.bearing, 1),
            "battery": round(self.battery, 1),
        }


def send_to_kafka(records, topic="gps-positions"):
    messages = "\n".join(json.dumps(r) for r in records)
    subprocess.run(
        ["bash", "-c",
         f"echo '{messages}' | "
         f"/opt/kafka/bin/kafka-console-producer.sh "
         f"--bootstrap-server kafka:9092 --topic {topic} "
         f"--property parse.key=false 2>/dev/null"],
        timeout=10,
        capture_output=True,
    )


def main():
    num_vehicles = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    interval = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    vehicles = [Vehicle(f"V{i:05d}") for i in range(num_vehicles)]
    total = 0

    print(f"Fleet simulator: {num_vehicles} vehicles, interval={interval}s")

    try:
        while True:
            batch = []
            for v in vehicles:
                v.move()
                batch.append(v.to_dict())
            send_to_kafka(batch)
            total += len(batch)
            print(f"  Sent {total} GPS positions ({len(batch)} vehicles)")
            time.sleep(interval)
    except KeyboardInterrupt:
        print(f"\nStopped. Total: {total} positions")


if __name__ == "__main__":
    main()
