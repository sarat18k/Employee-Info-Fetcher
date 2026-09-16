from typing import Any, Literal, TypedDict


class EmployeeRecord(TypedDict, total=False):
    name: str
    department: str
    role: str
    date_joined: str
    experience: str
    linkedin: str
    fun_fact: str


class FetchSuccess(TypedDict):
    status: Literal["success"]
    data: dict[str, Any]


class FetchError(TypedDict):
    status: Literal["error"]
    message: str


FetchResult = FetchSuccess | FetchError
