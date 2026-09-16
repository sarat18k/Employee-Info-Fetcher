import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

from employee_info_fetcher.audit import audit_event, get_correlation_id
from employee_info_fetcher.schemas import ProfileResponse
from employee_info_fetcher.service import ProfileService
from employee_info_fetcher.settings import get_settings

JobStatus = Literal["pending", "running", "completed", "failed"]


@dataclass
class JobRecord:
    id: str
    employee_name: str
    correlation_id: str
    status: JobStatus = "pending"
    result: ProfileResponse | None = None
    error: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class JobStore:
    def __init__(self, profile_service: ProfileService | None = None) -> None:
        self._service = profile_service or ProfileService()
        settings = get_settings()
        self._executor = ThreadPoolExecutor(max_workers=settings.job_worker_count)
        self._jobs: dict[str, JobRecord] = {}
        self._lock = threading.Lock()

    def submit(self, employee_name: str) -> JobRecord:
        job = JobRecord(
            id=str(uuid.uuid4()),
            employee_name=employee_name.strip(),
            correlation_id=get_correlation_id(),
        )
        with self._lock:
            self._jobs[job.id] = job
        self._executor.submit(self._run_job, job.id)
        audit_event("job.submitted", employee_name=job.employee_name, status=job.status)
        return job

    def get(self, job_id: str) -> JobRecord | None:
        with self._lock:
            job = self._jobs.get(job_id)
            return job

    def _run_job(self, job_id: str) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return
            job.status = "running"
            job.updated_at = datetime.now(timezone.utc)

        try:
            result = self._service.generate_profile(job.employee_name)
        except Exception as exc:
            with self._lock:
                job = self._jobs.get(job_id)
                if job is None:
                    return
                job.status = "failed"
                job.error = str(exc)
                job.updated_at = datetime.now(timezone.utc)
                failed_name = job.employee_name
            audit_event(
                "job.failed",
                employee_name=failed_name,
                status="failed",
            )
            return

        with self._lock:
            job = self._jobs[job_id]
            job.status = "completed"
            job.result = result
            job.updated_at = datetime.now(timezone.utc)
        audit_event(
            "job.completed",
            employee_name=job.employee_name,
            status="completed",
        )
