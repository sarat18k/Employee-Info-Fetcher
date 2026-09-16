from employee_info_fetcher.service import ProfileService


def test_dry_run(settings_with_data_file):
    service = ProfileService()
    result = service.dry_run("John Doe")
    assert result.employee["name"] == "John Doe"
    assert result.correlation_id
