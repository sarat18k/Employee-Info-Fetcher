import logging
import time
from dataclasses import dataclass
from typing import Any

from employee_info_fetcher.audit import audit_event, get_correlation_id
from employee_info_fetcher.employee_data import list_employee_names, resolve_employee
from employee_info_fetcher.exceptions import EmployeeDataError, EmployeeNotFoundError
from employee_info_fetcher.schemas import ProfileMetadata, ProfileResponse
from employee_info_fetcher.settings import Settings, get_settings
from employee_info_fetcher.tasks import build_crew

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DryRunProfile:
    correlation_id: str
    employee: dict[str, Any]
    message: str


class ProfileService:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def list_employees(self) -> list[str]:
        audit_event("employee.list.requested")
        names = list_employee_names()
        audit_event("employee.list.completed", count=len(names))
        return names

    def resolve(self, name: str) -> dict[str, Any]:
        return resolve_employee(name)

    def dry_run(self, name: str) -> DryRunProfile:
        employee = resolve_employee(name)
        audit_event(
            "profile.dry_run",
            employee_name=employee.get("name", name),
            status="success",
        )
        return DryRunProfile(
            correlation_id=get_correlation_id(),
            employee=employee,
            message="Dry run: crew skipped; employee record validated.",
        )

    def generate_profile(self, name: str) -> ProfileResponse:
        started = time.perf_counter()
        employee = resolve_employee(name)
        display_name = str(employee.get("name", name))

        audit_event("profile.generation.started", employee_name=display_name)

        try:
            self._settings.require_openai_key()
            crew = build_crew(employee, verbose=self._settings.crew_verbose)
            summary = str(crew.kickoff())
        except Exception as e:
            audit_event(
                "profile.generation.failed",
                employee_name=display_name,
                status="error",
            )
            logger.exception("Profile generation failed for %s", display_name)
            raise RuntimeError(f"Profile generation failed: {e}") from e

        duration_ms = int((time.perf_counter() - started) * 1000)
        audit_event(
            "profile.generation.completed",
            employee_name=display_name,
            status="success",
            duration_ms=duration_ms,
        )

        return ProfileResponse(
            correlation_id=get_correlation_id(),
            employee=ProfileMetadata(
                name=display_name,
                department=employee.get("department"),
                role=employee.get("role"),
            ),
            summary=summary,
        )


def map_service_error(exc: Exception) -> tuple[int, str]:
    if isinstance(exc, EmployeeNotFoundError):
        return 404, str(exc)
    if isinstance(exc, EmployeeDataError):
        return 503, str(exc)
    if isinstance(exc, ValueError):
        return 400, str(exc)
    if isinstance(exc, RuntimeError):
        return 502, str(exc)
    return 500, "Internal server error"
