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

## Structure du Projet
```
src/
├── simulator/          # Flotte 1000 véhicules
├── streaming/          # Spark Streaming → H3 → ClickHouse
├── batch/              # Airflow DAGs analytiques
├── api/                # Geofencing + ETA endpoints
├── kepler/             # Kepler.gl configuration
├── notebooks/          # Analyse et feature engineering
tests/                  # Tests unitaires et d'intégration
infra/                  # Configuration Terraform
```

## Prise en Main & Lancement

### 1. Démarrer l'infrastructure locale
```bash
docker-compose up -d
```

### 2. Déployer l'infrastructure Cloud avec Terraform
```bash
cd infra/terraform
terraform init
terraform apply -auto-approve
```

### 3. Lancer le simulateur de flotte de véhicules
```bash
python src/simulator/fleet_simulator.py
```

### 4. Lancer le job Spark Streaming d'agrégation H3
```bash
python src/streaming/h3_aggregation.py
```

### 5. Lancer l'API de Geofencing
```bash
uvicorn src.api.geofence_api:app --host 0.0.0.0 --port 8000
```

## Exécuter les Tests
Les tests couvrent les fonctions H3, le simulateur, l'API et l'intégration :
```bash
pytest tests/
```

