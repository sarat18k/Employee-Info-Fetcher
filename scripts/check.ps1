# Run lint and tests (from project root)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

$python = Join-Path $PWD "venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $python = "python"
}

& $python -m pip install -e ".[dev,api,db]" -q
& $python -m ruff check src tests
& $python -m pytest -q tests
Write-Host "All checks passed."
