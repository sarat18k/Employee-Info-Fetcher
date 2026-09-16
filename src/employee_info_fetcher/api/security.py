from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer

from employee_info_fetcher.audit import get_correlation_id
from employee_info_fetcher.auth.oidc import validate_oidc_token
from employee_info_fetcher.settings import Settings, get_settings

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
_bearer = HTTPBearer(auto_error=False)


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=401,
        detail=detail,
        headers={"X-Correlation-ID": get_correlation_id()},
    )


def _auth_bypassed(settings: Settings) -> bool:
    return not settings.is_production and not settings.service_api_key and not settings.oidc_issuer


def verify_auth(
    api_key: str | None = Security(_api_key_header),
    credentials: HTTPAuthorizationCredentials | None = Security(_bearer),
    settings: Settings | None = None,
) -> None:
    settings = settings or get_settings()

    if _auth_bypassed(settings):
        return

    if api_key and settings.service_api_key:
        expected = settings.service_api_key.get_secret_value()
        if api_key == expected:
            return

    if credentials and credentials.scheme.lower() == "bearer":
        token = credentials.credentials
        if settings.service_api_key and token == settings.service_api_key.get_secret_value():
            return
        if settings.oidc_issuer and settings.oidc_audience:
            try:
                validate_oidc_token(token, settings)
                return
            except Exception as exc:
                raise _unauthorized(f"Invalid bearer token: {exc}") from exc

    if settings.is_production and not settings.service_api_key and not settings.oidc_issuer:
        raise HTTPException(
            status_code=503,
            detail="Authentication is not configured",
            headers={"X-Correlation-ID": get_correlation_id()},
        )

    raise _unauthorized("Invalid or missing credentials (X-API-Key or Bearer token)")


# Backward-compatible alias
verify_api_key = verify_auth
