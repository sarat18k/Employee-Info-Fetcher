import hashlib


def redact_name(name: str) -> str:
    digest = hashlib.sha256(name.strip().lower().encode("utf-8")).hexdigest()[:12]
    return f"employee:{digest}"
