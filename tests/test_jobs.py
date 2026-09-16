import time

from employee_info_fetcher.jobs.store import JobStore
from employee_info_fetcher.schemas import ProfileMetadata, ProfileResponse
from employee_info_fetcher.service import ProfileService


class _StubProfileService(ProfileService):
    def generate_profile(self, name: str) -> ProfileResponse:
        return ProfileResponse(
            correlation_id="test-correlation",
            employee=ProfileMetadata(name=name, department="Engineering", role="Engineer"),
            summary="stub summary",
        )


def test_async_job_completes(settings_with_data_file):
    store = JobStore(profile_service=_StubProfileService())
    job = store.submit("John Doe")

    deadline = time.time() + 5
    while time.time() < deadline:
        current = store.get(job.id)
        assert current is not None
        if current.status in {"completed", "failed"}:
            break
        time.sleep(0.05)

    final = store.get(job.id)
    assert final is not None
    assert final.status == "completed"
    assert final.result is not None
    assert final.result.summary == "stub summary"
