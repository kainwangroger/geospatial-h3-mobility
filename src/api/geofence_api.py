"""
API Geofencing + ETA.

Endpoints:
  GET /health
  POST /geofence/check  - Vérifie si un point est dans une zone
  POST /geofence/zones   - Liste les zones
  GET  /eta              - Calcule ETA entre deux points
"""

import math

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Geospatial API", version="1.0")


GEOFENCE_ZONES = {
    "paris_centre": {"lat": 48.8566, "lon": 2.3522, "radius_km": 2.0},
    "aeroport_cdg": {"lat": 49.0097, "lon": 2.5479, "radius_km": 5.0},
    "la_defense": {"lat": 48.8917, "lon": 2.2389, "radius_km": 1.5},
    "versailles": {"lat": 48.8049, "lon": 2.1204, "radius_km": 3.0},
    "disneyland": {"lat": 48.8674, "lon": 2.7830, "radius_km": 4.0},
}


class Point(BaseModel):
    lat: float
    lon: float


class GeofenceCheck(BaseModel):
    point: Point
    zone_name: str


class GeofenceResult(BaseModel):
    inside: bool
    zone_name: str
    distance_km: float


GeoZone = dict


def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


@app.get("/health")
def health():
    return {"status": "ok", "zones_loaded": len(GEOFENCE_ZONES)}


@app.get("/geofence/zones")
def list_zones():
    return {"zones": list(GEOFENCE_ZONES.keys())}


@app.post("/geofence/check", response_model=GeofenceResult)
def check_geofence(req: GeofenceCheck):
    zone = GEOFENCE_ZONES.get(req.zone_name)
    if not zone:
        raise HTTPException(status_code=404, detail=f"Zone '{req.zone_name}' not found")

    dist = haversine(req.point.lat, req.point.lon, zone["lat"], zone["lon"])
    return GeofenceResult(
        inside=dist <= zone["radius_km"],
        zone_name=req.zone_name,
        distance_km=round(dist, 3),
    )


class ETARequest(BaseModel):
    origin: Point
    destination: Point
    vehicle_type: str = "car"


class ETAResult(BaseModel):
    distance_km: float
    duration_min: float
    vehicle_type: str


@app.post("/eta", response_model=ETAResult)
def calculate_eta(req: ETARequest):
    dist = haversine(req.origin.lat, req.origin.lon, req.destination.lat, req.destination.lon)
    avg_speeds = {"car": 35, "scooter": 20, "bike": 15, "pedestrian": 5}
    speed = avg_speeds.get(req.vehicle_type, 30)
    duration = (dist / speed) * 60
    return ETAResult(
        distance_km=round(dist, 2),
        duration_min=round(duration, 1),
        vehicle_type=req.vehicle_type,
    )
