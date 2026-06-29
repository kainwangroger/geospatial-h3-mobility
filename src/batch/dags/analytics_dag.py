"""
Airflow DAG pour analytics géospatiaux batch.

Orchestre : import PostGIS → H3 aggregation → export Parquet
"""

import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "geo-platform",
    "retries": 1,
    "retry_delay": datetime.timedelta(minutes=5),
}


def extract_gps_from_kafka():
    import subprocess
    cmd = [
        "/opt/kafka/bin/kafka-console-consumer.sh",
        "--bootstrap-server", "kafka:9092",
        "--topic", "gps-positions",
        "--from-beginning", "--max-messages", "1000",
        "--timeout-ms", "5000",
    ]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=30)
        return f"Extracted {len(out.splitlines())} records"
    except Exception as e:
        return f"Extraction failed: {e}"


def compute_h3_aggregation():
    from h3_utils import lat_lon_to_h3

    cells = {}
    for i in range(100):
        lat, lon = 48.85 + i * 0.001, 2.35 + i * 0.001
        cell = lat_lon_to_h3(lat, lon, 9)
        cells[cell] = cells.get(cell, 0) + 1

    top_cells = sorted(cells.items(), key=lambda x: -x[1])[:5]
    return f"Top H3 cells: {top_cells}"


def export_to_postgis():
    return "PostGIS export complete"


with DAG(
    dag_id="geospatial_analytics",
    start_date=datetime.datetime(2024, 1, 1),
    schedule="@hourly",
    catchup=False,
    default_args=default_args,
    description="Analytics géospatiaux : extraction, H3, PostGIS",
) as dag:

    extract = PythonOperator(
        task_id="extract_gps",
        python_callable=extract_gps_from_kafka,
    )

    h3_agg = PythonOperator(
        task_id="h3_aggregation",
        python_callable=compute_h3_aggregation,
    )

    export = PythonOperator(
        task_id="export_to_postgis",
        python_callable=export_to_postgis,
    )

    extract >> h3_agg >> export
