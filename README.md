# 6. Pipeline de Données Géospatiales (Mobility/Location Intelligence)

**Stack :** Kafka, Spark, H3 (Uber), PostGIS/ClickHouse, Kepler.gl, Airflow  
**Niveau :** Avancé | **Volume :** 100M+ points GPS/jour | **Contexte :** 100K véhicules trackés

## Contexte Métier
Entreprise de mobilité (VTC, livraison) tracke 100K véhicules en temps réel.

## Ce que tu dois construire

### Simulateur de Flotte
- 1000 véhicules émettant leur position GPS toutes les 5 secondes
- Types : voiture, scooter, vélo, piéton
- Routes simulées sur une vraie carte (OpenStreetMap)

### 3 Pipelines Parallèles
- **Temps réel** : Spark Streaming → agrégation H3 → ClickHouse (latence < 1s)
- **Batch** : Airflow → Spark → jointure métier → PostGIS (analytics)
- **ML** : Feature extraction géospatiale → Parquet → training

### Spatial Analytics
- H3 Hexagonal Indexing (résolutions 8 à 12)
- Heatmaps densité par hexagone
- Trajectory clustering
- Geofencing (alertes entrée/sortie de zone)
- ETA computation

### Visualisation Kepler.gl
- Carte interactive temps réel
- Filtres : zone, statut, temps
- Animation : lecture des trajectoires sur 24h

### Difficultés Techniques
- Grande cardinalité des clés H3
- Window operations complexes (trajectory stitching)
- Compression des séquences de points
- Tradeoff précision spatiale vs performance

## Structure attendue
```
src/
├── simulator/          # Flotte 1000 véhicules
├── streaming/          # Spark Streaming → H3 → ClickHouse
├── batch/              # Airflow DAGs analytiques
├── api/                # Geofencing + ETA endpoints
├── dashboard/          # Kepler.gl config
├── notebooks/          # Analyse et feature engineering
└── docker-compose.yml
```
