# Architecture

## Overview

```
CLI / API
   │
   ▼
ProfileService  ──►  EmployeeRepository (JSON or PostgreSQL)
   │
   ▼
Crew (sequential tasks)  ──►  OpenAI via CrewAI
```

## Layers

| Layer | Module | Responsibility |
|-------|--------|----------------|
| Interface | `cli.py`, `api/` | User/API entrypoints |
| Application | `service.py`, `jobs/` | Use cases, orchestration |
| Domain | `tasks.py`, `agents.py` | CrewAI workflow |
| Data | `repositories/`, `db/` | Employee persistence |
| Cross-cutting | `settings.py`, `audit.py`, `bootstrap.py` | Config, logging, startup |

## Profile generation flow

1. Resolve employee by name (repository lookup).
2. Build four specialist tasks with **field slices** (token-efficient).
3. Run tasks sequentially; manager synthesizes with prior task outputs as context.
4. Return structured `ProfileResponse` (API) or text/JSON (CLI).

## Async API jobs

`POST /v1/profiles/async` submits work to an in-process thread pool (`JobStore`).
Poll `GET /v1/jobs/{id}` for completion. Jobs are not persisted across process restarts.

## Configuration

Single source of truth: `settings.py` (environment variables + `.env`).

Run `employee-fetcher --doctor` before deploy to validate datastore and secrets.

## Extension points

- Add a repository backend (e.g. REST HRIS) by implementing `EmployeeRepository`.
- Attach `FetchEmployeeTool` to agents if tool-based retrieval is preferred.
- Swap `JobStore` for Redis/Celery for durable background processing.
