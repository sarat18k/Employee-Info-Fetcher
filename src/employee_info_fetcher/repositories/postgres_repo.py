from typing import Any

from sqlalchemy import func, select

from employee_info_fetcher.db.models import EmployeeRow
from employee_info_fetcher.db.session import db_session


class PostgresEmployeeRepository:
    def list_names(self) -> list[str]:
        with db_session() as session:
            rows = session.scalars(select(EmployeeRow.name).order_by(EmployeeRow.name)).all()
            return list(rows)

    def get_by_name(self, name: str) -> dict[str, Any] | None:
        key = name.strip().lower()
        if not key:
            return None
        with db_session() as session:
            row = session.scalar(
                select(EmployeeRow).where(func.lower(EmployeeRow.name) == key)
            )
            return row.to_dict() if row else None
