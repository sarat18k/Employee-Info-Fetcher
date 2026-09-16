from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EMPLOYEE_DATA_FILE = PROJECT_ROOT / "data" / "employees.json"

ENV_FILE = PROJECT_ROOT / ".env"
