# Employee Info Fetcher

Enterprise-oriented employee profile service powered by [CrewAI](https://crewai.com). CLI and REST API, JSON or PostgreSQL storage, async jobs, metrics, and audit logging.

## Why this structure

- **Repository pattern** — swap JSON for PostgreSQL without changing business logic
- **Service layer** — one code path for CLI and API
- **Field-scoped Crew tasks** — lower token use than sending full records to every agent
- **`--doctor`** — pre-flight checks before you run LLM workflows

See [Architecture](docs/ARCHITECTURE.md) and [Operations](docs/OPERATIONS.md).

## Quick start

```bash
python -m venv venv
venv\Scripts\activate
pip install -e ".[dev,api,db]"
copy .env.example .env
employee-fetcher --doctor
employee-fetcher --list
employee-fetcher-api
```

## Common commands

| Command | Purpose |
|---------|---------|
| `employee-fetcher --doctor` | Validate env + datastore |
| `employee-fetcher --list` | List employee names |
| `employee-fetcher --name "John Doe" --dry-run` | Lookup without LLM |
| `employee-fetcher --name "John Doe"` | Full CrewAI profile |
| `employee-fetcher-api` | Start REST API |
| `employee-fetcher-db seed` | Load JSON into PostgreSQL |

## PostgreSQL

```bash
set DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/employee_db
alembic upgrade head
employee-fetcher-db seed
employee-fetcher --doctor
```

## Development

```powershell
.\scripts\check.ps1
```

Or manually:

```bash
ruff check src tests
pytest -q
```

## License

MIT — see [LICENSE](LICENSE).
