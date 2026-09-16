import json

import pytest

from employee_info_fetcher.exceptions import EmployeeDataError
from employee_info_fetcher.repositories.factory import reset_repository_cache
from employee_info_fetcher.settings import get_settings


def test_rejects_incomplete_record(tmp_path, monkeypatch):
    path = tmp_path / "bad.json"
    path.write_text(json.dumps([{"name": "Jane"}]), encoding="utf-8")
    monkeypatch.setenv("EMPLOYEE_DATA_FILE", str(path))
    get_settings.cache_clear()
    reset_repository_cache()

    from employee_info_fetcher.employee_data import list_employee_names

    with pytest.raises(EmployeeDataError, match="missing required fields"):
        list_employee_names()

    get_settings.cache_clear()
    reset_repository_cache()
