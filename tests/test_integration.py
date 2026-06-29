import subprocess
import pytest

SERVICES = [
    "kafka", "postgis", "clickhouse",
    "spark-master", "spark-worker",
    "jupyter",
    "airflow-db", "airflow-webserver", "airflow-scheduler", "airflow-init",
    "api",
]


class TestDockerCompose:
    def test_docker_installed(self):
        result = subprocess.run(
            ["docker", "--version"], capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0
        assert "Docker" in result.stdout

    def test_compose_syntax(self):
        result = subprocess.run(
            ["docker", "compose", "-f", "docker-compose.yml", "config"],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"Compose config error: {result.stderr}"

    def test_compose_file_exists(self):
        import os
        assert os.path.isfile("docker-compose.yml")

    @pytest.mark.parametrize("service", SERVICES)
    def test_service_in_compose(self, service):
        result = subprocess.run(
            ["docker", "compose", "-f", "docker-compose.yml", "config", "--services"],
            capture_output=True, text=True, timeout=15,
        )
        assert result.returncode == 0
        assert service in result.stdout, f"Service '{service}' not found in compose"


class TestConfigFiles:
    def test_simulator_exists(self):
        import os
        assert os.path.isfile("src/simulator/fleet_simulator.py")

    def test_h3_utils_exists(self):
        import os
        assert os.path.isfile("src/streaming/h3_utils.py")

    def test_h3_aggregation_exists(self):
        import os
        assert os.path.isfile("src/streaming/h3_aggregation.py")

    def test_airflow_dag_exists(self):
        import os
        assert os.path.isfile("src/batch/dags/analytics_dag.py")

    def test_api_exists(self):
        import os
        assert os.path.isfile("src/api/geofence_api.py")

    def test_kepler_config_exists(self):
        import os
        assert os.path.isfile("src/kepler/config.py")

    def test_notebook_exists(self):
        import os
        assert os.path.isfile("src/notebooks/h3_analysis.py")
