import json
from pathlib import Path
from typing import Any

from employee_info_fetcher.constants import EMPLOYEE_REQUIRED_FIELDS
from employee_info_fetcher.exceptions import EmployeeDataError


class JsonEmployeeRepository:
    def __init__(self, data_file: Path) -> None:
        self._data_file = data_file
        self._index: dict[str, dict[str, Any]] | None = None
        self._mtime: float | None = None

    def _load_index(self) -> dict[str, dict[str, Any]]:
        if not self._data_file.is_file():
            raise EmployeeDataError(f"Employee data file not found: {self._data_file}")

        mtime = self._data_file.stat().st_mtime
        if self._index is not None and self._mtime == mtime:
            return self._index

        with self._data_file.open(encoding="utf-8") as f:
            raw = json.load(f)
        if not isinstance(raw, list):
            raise EmployeeDataError("Employee data must be a JSON array")

        index: dict[str, dict[str, Any]] = {}
        for index_no, entry in enumerate(raw, start=1):
            if not isinstance(entry, dict):
                raise EmployeeDataError(f"Record #{index_no} must be a JSON object")
            missing = [field for field in EMPLOYEE_REQUIRED_FIELDS if not entry.get(field)]
            if missing:
                raise EmployeeDataError(
                    f"Record #{index_no} missing required fields: {', '.join(missing)}"
                )
            emp_name = str(entry["name"]).strip()
            key = emp_name.lower()
            if key in index:
                raise EmployeeDataError(f"Duplicate employee name: {emp_name}")
            index[key] = entry

        self._index = index
        self._mtime = mtime
        return index

    def clear_cache(self) -> None:
        self._index = None
        self._mtime = None

    def list_names(self) -> list[str]:
        return sorted(record.get("name", "") for record in self._load_index().values())

    def get_by_name(self, name: str) -> dict[str, Any] | None:
        key = name.strip().lower()
        if not key:
            return None
        return self._load_index().get(key)
