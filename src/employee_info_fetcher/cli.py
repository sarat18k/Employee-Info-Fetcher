import argparse
import json
import sys

from employee_info_fetcher import __version__
from employee_info_fetcher.audit import audit_event, new_correlation_id
from employee_info_fetcher.bootstrap import bootstrap
from employee_info_fetcher.doctor import run_doctor
from employee_info_fetcher.service import ProfileService, map_service_error
from employee_info_fetcher.settings import get_settings

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_USAGE = 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="employee-fetcher",
        description="Fetch and summarize employee profiles with CrewAI.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "-n",
        "--name",
        help="Employee full name (interactive prompt if omitted)",
    )
    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="List employees in the knowledge base and exit",
    )
    parser.add_argument(
        "--doctor",
        action="store_true",
        help="Validate configuration and datastore connectivity",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate employee record without calling the LLM crew",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output",
    )
    return parser


def _emit_error(message: str, as_json: bool) -> None:
    if as_json:
        print(json.dumps({"status": "error", "message": message}))
    else:
        print(f"Error: {message}", file=sys.stderr)


def _print_doctor_report(as_json: bool) -> int:
    report = run_doctor()
    if as_json:
        print(
            json.dumps(
                {
                    "status": "ok" if report.ok else "error",
                    "checks": report.checks,
                    "warnings": report.warnings,
                    "errors": report.errors,
                }
            )
        )
    else:
        print("Environment check\n" + "-" * 40)
        for line in report.checks:
            print(f"  OK   {line}")
        for line in report.warnings:
            print(f"  WARN {line}")
        for line in report.errors:
            print(f"  ERR  {line}")
    return EXIT_OK if report.ok else EXIT_ERROR


def main(argv: list[str] | None = None) -> None:
    bootstrap()
    new_correlation_id()
    args = build_parser().parse_args(argv)
    service = ProfileService()
    settings = get_settings()

    if args.doctor:
        sys.exit(_print_doctor_report(args.json))

    if args.list:
        try:
            names = service.list_employees()
        except Exception as exc:
            _, detail = map_service_error(exc)
            _emit_error(detail, args.json)
            sys.exit(EXIT_ERROR)
        if args.json:
            print(json.dumps({"employees": names, "count": len(names)}))
        else:
            if not names:
                print("No employees in knowledge base.")
                sys.exit(EXIT_OK)
            print("Available employees:")
            for name in names:
                print(f"  - {name}")
        sys.exit(EXIT_OK)

    employee_name = (args.name or input("Enter employee name: ")).strip()
    if not employee_name:
        _emit_error("No name entered.", args.json)
        sys.exit(EXIT_USAGE)

    if args.dry_run:
        try:
            result = service.dry_run(employee_name)
        except Exception as exc:
            _, detail = map_service_error(exc)
            _emit_error(detail, args.json)
            sys.exit(EXIT_ERROR)
        if args.json:
            print(
                json.dumps(
                    {
                        "status": "ok",
                        "correlation_id": result.correlation_id,
                        "message": result.message,
                        "employee": result.employee,
                    }
                )
            )
        else:
            print(result.message)
            print(json.dumps(result.employee, indent=2))
        sys.exit(EXIT_OK)

    try:
        settings.require_openai_key()
    except ValueError as exc:
        _emit_error(str(exc), args.json)
        sys.exit(EXIT_ERROR)

    audit_event("cli.profile.requested", employee_name=employee_name)

    try:
        profile = service.generate_profile(employee_name)
    except Exception as exc:
        _, detail = map_service_error(exc)
        _emit_error(detail, args.json)
        sys.exit(EXIT_ERROR)

    if args.json:
        print(json.dumps(profile.model_dump()))
    else:
        print(f"\nFound {profile.employee.name} in records.\n")
        print("Final summary for employee:")
        print("-" * 50)
        print(profile.summary)

    sys.exit(EXIT_OK)
