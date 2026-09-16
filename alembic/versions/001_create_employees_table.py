"""create employees table

Revision ID: 001
Revises:
Create Date: 2026-03-25
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "employees",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("department", sa.String(length=120), nullable=True),
        sa.Column("role", sa.String(length=120), nullable=True),
        sa.Column("date_joined", sa.String(length=32), nullable=True),
        sa.Column("experience", sa.Text(), nullable=True),
        sa.Column("linkedin", sa.String(length=512), nullable=True),
        sa.Column("fun_fact", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_employees_name"), "employees", ["name"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_employees_name"), table_name="employees")
    op.drop_table("employees")
