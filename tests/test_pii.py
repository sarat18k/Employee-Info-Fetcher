from employee_info_fetcher.pii import redact_name


def test_redact_name_is_stable_and_non_reversible():
    first = redact_name("John Doe")
    second = redact_name("John Doe")
    assert first == second
    assert first.startswith("employee:")
    assert "John" not in first
