from employee_info_fetcher.doctor import run_doctor


def test_doctor_passes_with_json_store(settings_with_data_file):
    report = run_doctor()
    assert report.ok
    assert any("Employee records indexed" in line for line in report.checks)


def test_doctor_warns_without_openai_key(settings_with_data_file, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "")
    from employee_info_fetcher.settings import get_settings

    get_settings.cache_clear()
    report = run_doctor()
    assert any("OPENAI_API_KEY" in warning for warning in report.warnings)
    get_settings.cache_clear()
