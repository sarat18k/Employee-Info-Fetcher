import pytest

from employee_info_fetcher.employee_data import (
    list_employee_names,
    lookup_employee,
    resolve_employee,
)
from employee_info_fetcher.exceptions import EmployeeNotFoundError


def test_lookup_employee_case_insensitive(settings_with_data_file):
    record = lookup_employee("john doe")
    assert record is not None
    assert record["department"] == "Engineering"


def test_resolve_employee_not_found(settings_with_data_file):
    with pytest.raises(EmployeeNotFoundError):
        resolve_employee("Missing Person")


def test_list_employee_names(settings_with_data_file):
    assert list_employee_names() == ["John Doe"]
