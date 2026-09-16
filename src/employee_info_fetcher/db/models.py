from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class EmployeeRow(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    department: Mapped[str | None] = mapped_column(String(120))
    role: Mapped[str | None] = mapped_column(String(120))
    date_joined: Mapped[str | None] = mapped_column(String(32))
    experience: Mapped[str | None] = mapped_column(Text())
    linkedin: Mapped[str | None] = mapped_column(String(512))
    fun_fact: Mapped[str | None] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "department": self.department or "",
            "role": self.role or "",
            "date_joined": self.date_joined or "",
            "experience": self.experience or "",
            "linkedin": self.linkedin or "",
            "fun_fact": self.fun_fact or "",
        }
