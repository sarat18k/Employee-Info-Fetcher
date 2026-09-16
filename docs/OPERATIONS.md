# Operations Guide

## Pre-flight check

```bash
employee-fetcher --doctor
employee-fetcher --doctor --json
```

## Configuration

See `.env.example` for all variables.

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | PostgreSQL DSN (`postgresql+psycopg://...`). Omit to use JSON file store. |
| `SERVICE_API_KEY` | API key for `/v1/*` (`X-API-Key` header) |
| `OIDC_ISSUER` / `OIDC_AUDIENCE` | Optional Bearer JWT validation via IdP JWKS |
| `RATE_LIMIT` | slowapi limit for protected routes (default `60/minute`) |
| `REDACT_PII_LOGS` | Hash employee names in audit logs (auto-enabled in production) |
| `JOB_WORKER_COUNT` | Thread pool size for async profile jobs |

## Data stores

### JSON (default)

`data/employees.json` — no migration required.

### PostgreSQL

Install PostgreSQL locally or use a managed instance, then:

```bash
pip install -e ".[db,api]"
export DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/employee_db
alembic upgrade head
employee-fetcher-db seed
```

## API

```bash
pip install -e ".[api,db]"
employee-fetcher-api
```

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Liveness |
| GET | `/health/ready` | No | Readiness (+ DB ping when configured) |
| GET | `/metrics` | No | Prometheus metrics |
| GET | `/v1/employees` | Yes | List names |
| POST | `/v1/profiles` | Yes | Sync profile generation |
| POST | `/v1/profiles/async` | Yes | Returns `job_id` |
| GET | `/v1/jobs/{job_id}` | Yes | Poll async job |

Auth: `X-API-Key: ...` or `Authorization: Bearer <token>` (service key or OIDC JWT).

## Observability

- Structured JSON logs (`LOG_FORMAT=json`)
- Audit events: `profile.generation.*`, `job.*`, `employee.list.*`
- Prometheus scrape `/metrics`
- `X-Correlation-ID` on every HTTP response

## CI

```bash
ruff check src tests
pytest -q
```
