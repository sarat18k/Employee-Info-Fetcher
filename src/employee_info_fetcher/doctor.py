from dataclasses import dataclass, field

from sqlalchemy import text

from employee_info_fetcher import __version__
from employee_info_fetcher.employee_data import list_employee_names
from employee_info_fetcher.settings import Settings, get_settings


@dataclass
class DoctorReport:
    ok: bool = True
    checks: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def add_ok(self, message: str) -> None:
        self.checks.append(message)

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.ok = False


def run_doctor(settings: Settings | None = None) -> DoctorReport:
    settings = settings or get_settings()
    report = DoctorReport()
    report.add_ok(f"employee-info-fetcher v{__version__} ({settings.app_env})")

    if settings.use_database:
        dsn_tail = (settings.database_url or "").split("@")[-1]
        report.add_ok(f"Datastore: PostgreSQL ({dsn_tail})")
        try:
            from employee_info_fetcher.db.session import db_session

            with db_session() as session:
                session.execute(text("SELECT 1"))
            report.add_ok("Database connection successful")
            try:
                count = len(list_employee_names())
                report.add_ok(f"Employee records available: {count}")
            except Exception as exc:
                report.add_error(f"Employee query failed: {exc}")
        except Exception as exc:
            report.add_error(f"Database connection failed: {exc}")
    else:
        report.add_ok(f"Datastore: JSON ({settings.employee_data_file})")
        if settings.employee_data_file.is_file():
            report.add_ok("Employee JSON file found")
            try:
                count = len(list_employee_names())
                report.add_ok(f"Employee records indexed: {count}")
            except Exception as exc:
                report.add_error(f"Employee index failed: {exc}")
        else:
            report.add_error(f"Employee JSON file missing: {settings.employee_data_file}")

    if settings.openai_api_key and settings.openai_api_key.get_secret_value().strip():
        report.add_ok(f"OpenAI configured (model: {settings.openai_model})")
    else:
        report.add_warning("OPENAI_API_KEY not set — profile generation will fail")

    if settings.is_production:
        if settings.service_api_key or (settings.oidc_issuer and settings.oidc_audience):
            report.add_ok("API authentication configured for production")
        else:
            report.add_error("Production requires SERVICE_API_KEY or OIDC_ISSUER/OIDC_AUDIENCE")
    elif settings.service_api_key:
        report.add_ok("SERVICE_API_KEY configured")
    else:
        report.add_warning("SERVICE_API_KEY not set — API auth bypassed in development")

    return report
