import time
from functools import lru_cache
from typing import Any

import httpx
import jwt
from jwt import PyJWKClient

from employee_info_fetcher.settings import Settings


@lru_cache
def _jwks_client_for_issuer(issuer: str) -> PyJWKClient:
    issuer = issuer.rstrip("/")
    discovery_url = f"{issuer}/.well-known/openid-configuration"
    with httpx.Client(timeout=10.0) as client:
        response = client.get(discovery_url)
        response.raise_for_status()
        jwks_uri = response.json()["jwks_uri"]
    return PyJWKClient(jwks_uri)


def validate_oidc_token(token: str, settings: Settings) -> dict[str, Any]:
    if not settings.oidc_issuer or not settings.oidc_audience:
        raise ValueError("OIDC is not configured")

    issuer = settings.oidc_issuer.rstrip("/")
    client = _jwks_client_for_issuer(issuer)
    signing_key = client.get_signing_key_from_jwt(token)
    claims = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256", "ES256"],
        audience=settings.oidc_audience,
        issuer=issuer,
        options={"require": ["exp", "iss", "aud"]},
    )
    if claims.get("exp", 0) < time.time():
        raise ValueError("Token expired")
    return claims
