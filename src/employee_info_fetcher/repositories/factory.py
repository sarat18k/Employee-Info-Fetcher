from employee_info_fetcher.repositories.base import EmployeeRepository
from employee_info_fetcher.repositories.json_repo import JsonEmployeeRepository
from employee_info_fetcher.settings import get_settings

_json_repo_singleton: JsonEmployeeRepository | None = None


def get_employee_repository() -> EmployeeRepository:
    settings = get_settings()
    if settings.database_url:
        from employee_info_fetcher.repositories.postgres_repo import PostgresEmployeeRepository

        return PostgresEmployeeRepository()

    global _json_repo_singleton
    if _json_repo_singleton is None:
        _json_repo_singleton = JsonEmployeeRepository(settings.employee_data_file)
    return _json_repo_singleton


def reset_repository_cache() -> None:
    global _json_repo_singleton
    if _json_repo_singleton is not None:
        _json_repo_singleton.clear_cache()
    _json_repo_singleton = None
