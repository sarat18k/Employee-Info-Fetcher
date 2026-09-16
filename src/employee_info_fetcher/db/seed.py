import json
from pathlib import Path

from sqlalchemy import select

from employee_info_fetcher.db.models import EmployeeRow
from employee_info_fetcher.db.session import db_session


def seed_employees_from_json(source_file: Path) -> int:
    with source_file.open(encoding="utf-8") as f:
        rows = json.load(f)
    if not isinstance(rows, list):
        raise ValueError("Seed file must contain a JSON array")

    upserted = 0
    with db_session() as session:
        for item in rows:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name", "")).strip()
            if not name:
                continue
            existing = session.scalar(
                select(EmployeeRow).where(EmployeeRow.name == name)
            )
            payload = {
                "department": item.get("department"),
                "role": item.get("role"),
                "date_joined": item.get("date_joined"),
                "experience": item.get("experience"),
                "linkedin": item.get("linkedin"),
                "fun_fact": item.get("fun_fact"),
            }
            if existing:
                for key, value in payload.items():
                    setattr(existing, key, value)
            else:
                session.add(EmployeeRow(name=name, **payload))
            upserted += 1
    return upserted
