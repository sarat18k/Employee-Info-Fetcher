import logging
import uuid
from contextvars import ContextVar
from typing import Any

from employee_info_fetcher.pii import redact_name
from employee_info_fetcher.settings import get_settings

logger = logging.getLogger("employee_info_fetcher.audit")

correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")


def new_correlation_id() -> str:
    cid = str(uuid.uuid4())
    correlation_id_var.set(cid)
    return cid


def get_correlation_id() -> str:
    return correlation_id_var.get() or new_correlation_id()


def _sanitize_fields(fields: dict[str, Any]) -> dict[str, Any]:
    if not get_settings().redact_pii_logs:
        return fields
    sanitized = dict(fields)
    if "employee_name" in sanitized and isinstance(sanitized["employee_name"], str):
        sanitized["employee_name"] = redact_name(sanitized["employee_name"])
    return sanitized


def audit_event(event: str, **fields: Any) -> None:
    safe_fields = _sanitize_fields(fields)
    logger.info(
        event,
        extra={
            "audit_event": event,
            "correlation_id": get_correlation_id(),
            **safe_fields,
        },
    )
