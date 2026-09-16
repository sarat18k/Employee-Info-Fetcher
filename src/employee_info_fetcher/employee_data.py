from typing import Any

from employee_info_fetcher.exceptions import EmployeeDataError, EmployeeNotFoundError
from employee_info_fetcher.repositories.factory import (
    get_employee_repository,
    reset_repository_cache,
)
from employee_info_fetcher.types import FetchError, FetchResult, FetchSuccess


def clear_employee_index_cache() -> None:
    """Backward-compatible name for tests."""
    reset_repository_cache()


def list_employee_names() -> list[str]:
    return get_employee_repository().list_names()


def lookup_employee(name: str) -> dict[str, Any] | None:
    return get_employee_repository().get_by_name(name)


def fetch_employee_result(name: str) -> FetchResult:
    try:
        record = lookup_employee(name)
    except EmployeeDataError as e:
        return FetchError(status="error", message=str(e))
    if record is None:
        return FetchError(status="error", message="Employee not found")
    return FetchSuccess(status="success", data=record)


def resolve_employee(name: str) -> dict[str, Any]:
    try:
        record = lookup_employee(name)
    except EmployeeDataError:
        raise
    if record is None:
        raise EmployeeNotFoundError("Employee not found")
    return record
