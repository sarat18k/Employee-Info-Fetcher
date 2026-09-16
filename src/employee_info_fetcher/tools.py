import json
import logging

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from employee_info_fetcher.employee_data import fetch_employee_result

logger = logging.getLogger(__name__)


class EmployeeToolInput(BaseModel):
    name: str = Field(..., description="Full name of the employee")


class FetchEmployeeTool(BaseTool):
    name: str = "fetch_employee"
    description: str = "Retrieve employee data by name from internal knowledge base"
    args_schema: type[BaseModel] = EmployeeToolInput

    def _run(self, name: str) -> str:
        logger.info("Fetching employee data for: %s", name)
        return json.dumps(fetch_employee_result(name), indent=2)
