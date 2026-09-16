import json
from pathlib import Path

import pytest

from employee_info_fetcher.repositories.factory import reset_repository_cache
from employee_info_fetcher.settings import get_settings


@pytest.fixture
def sample_employees_file(tmp_path: Path) -> Path:
    data = [
        {
            "name": "John Doe",
            "department": "Engineering",
            "role": "Software Engineer",
            "date_joined": "2023-11-10",
            "experience": "Acme Corp",
            "linkedin": "https://linkedin.com/in/johndoe",
            "fun_fact": "Bikes",
        }
    ]
    path = tmp_path / "employees.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


@pytest.fixture
def settings_with_data_file(sample_employees_file: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("EMPLOYEE_DATA_FILE", str(sample_employees_file))
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    get_settings.cache_clear()
    reset_repository_cache()
    yield
    get_settings.cache_clear()
    reset_repository_cache()
