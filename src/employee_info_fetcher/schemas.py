from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str
    environment: str
    version: str


class EmployeeListResponse(BaseModel):
    employees: list[str]
    count: int


class ProfileRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)


class ProfileMetadata(BaseModel):
    name: str
    department: str | None = None
    role: str | None = None


class ProfileResponse(BaseModel):
    correlation_id: str
    employee: ProfileMetadata
    summary: str


class ErrorResponse(BaseModel):
    detail: str
    correlation_id: str | None = None


class JobSubmitResponse(BaseModel):
    job_id: str
    status: str
    correlation_id: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    correlation_id: str
    employee_name: str
    result: ProfileResponse | None = None
    error: str | None = None


class ReadinessResponse(BaseModel):
    status: str
    datastore: str
