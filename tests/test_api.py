import pytest
from fastapi.testclient import TestClient

from employee_info_fetcher.api.app import create_app
from employee_info_fetcher.settings import get_settings


@pytest.fixture
def api_client(settings_with_data_file, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("SERVICE_API_KEY", "test-key")
    get_settings.cache_clear()
    with TestClient(create_app()) as client:
        yield client
    get_settings.cache_clear()


def test_health(api_client: TestClient):
    response = api_client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "X-Correlation-ID" in response.headers


def test_readiness(api_client: TestClient):
    response = api_client.get("/health/ready")
    assert response.status_code == 200
    assert response.json()["datastore"] == "json"


def test_list_employees_requires_api_key(api_client: TestClient):
    response = api_client.get("/v1/employees")
    assert response.status_code == 401


def test_list_employees_success(api_client: TestClient):
    response = api_client.get("/v1/employees", headers={"X-API-Key": "test-key"})
    assert response.status_code == 200
    assert response.json()["count"] == 1


def test_metrics(api_client: TestClient):
    response = api_client.get("/metrics")
    assert response.status_code == 200
