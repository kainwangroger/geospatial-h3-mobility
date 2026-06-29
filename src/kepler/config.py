"""
Configuration Kepler.gl pour la visualisation géospatiale.

Génère une configuration exportable pour Kepler.gl.
"""

KEPLER_CONFIG = {
    "version": "v1",
    "config": {
        "visState": {
            "filters": [
                {
                    "dataId": ["gps_positions"],
                    "id": "vehicle_type_filter",
                    "name": ["type"],
                    "type": "multiSelect",
                    "value": ["car", "scooter", "bike", "pedestrian"],
                    "enlarge": False,
                },
                {
                    "dataId": ["gps_positions"],
                    "id": "status_filter",
                    "name": ["status"],
                    "type": "multiSelect",
                    "value": ["active"],
                    "enlarge": False,
                },
            ],
            "layers": [
                {
                    "id": "vehicle_points",
                    "type": "point",
                    "config": {
                        "dataId": "gps_positions",
                        "label": "Véhicules",
                        "color": [18, 147, 154],
                        "columns": {"lat": "lat", "lng": "lon", "altitude": "altitude"},
                        "isVisible": True,
                        "visConfig": {
                            "radius": 4,
                            "opacity": 0.8,
                            "outline": False,
                            "colorField": {"name": ["type"], "type": "string"},
                        },
                    },
                },
                {
                    "id": "h3_hexagons",
                    "type": "hexagonId",
                    "config": {
                        "dataId": "h3_aggregation",
                        "label": "Densité H3",
                        "color": [255, 153, 31],
                        "columns": {"hex_id": "h3_cell"},
                        "isVisible": True,
                        "visConfig": {
                            "opacity": 0.6,
                            "colorRange": {
                                "name": "Global Warming",
                                "type": "sequential",
                                "category": "Uber",
                            },
                            "enable3d": True,
                            "heightField": {"name": ["num_points"], "type": "integer"},
                        },
                    },
                },
            ],
            "interactionConfig": {
                "tooltip": {
                    "fieldsToShow": {
                        "gps_positions": [
                            {"name": "vehicle_id"},
                            {"name": "type"},
                            {"name": "speed"},
                            {"name": "status"},
                        ],
                    },
                    "enabled": True,
                },
            },
            "layerOrder": [0, 1],
        },
        "mapState": {
            "latitude": 48.8566,
            "longitude": 2.3522,
            "zoom": 11,
            "pitch": 0,
            "bearing": 0,
        },
        "mapStyle": {
            "styleType": "dark",
            "topLayerGroups": {},
            "visibleLayerGroups": {
                "label": True,
                "road": True,
                "border": False,
                "building": True,
                "water": True,
                "land": True,
                "3d building": False,
            },
        },
    },
}


def export_config():
    import json
    return json.dumps(KEPLER_CONFIG, indent=2)


if __name__ == "__main__":
    print(export_config())
