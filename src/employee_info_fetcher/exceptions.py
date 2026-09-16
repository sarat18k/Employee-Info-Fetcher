class EmployeeDataError(Exception):
    """Raised when the knowledge base is missing or invalid."""


class EmployeeNotFoundError(Exception):
    """Raised when no employee matches the given name."""
