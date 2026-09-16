from typing import Any, Protocol


class EmployeeRepository(Protocol):
    def list_names(self) -> list[str]: ...

    def get_by_name(self, name: str) -> dict[str, Any] | None: ...
