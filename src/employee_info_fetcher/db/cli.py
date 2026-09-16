import argparse
import sys
from pathlib import Path

from employee_info_fetcher.bootstrap import bootstrap
from employee_info_fetcher.db.seed import seed_employees_from_json
from employee_info_fetcher.settings import get_settings


def main(argv: list[str] | None = None) -> None:
    bootstrap()
    settings = get_settings()
    parser = argparse.ArgumentParser(description="Database utilities")
    sub = parser.add_subparsers(dest="command", required=True)

    seed_parser = sub.add_parser("seed", help="Seed employees from JSON into PostgreSQL")
    seed_parser.add_argument(
        "--file",
        default=str(settings.employee_data_file),
        help="Path to employees JSON file",
    )

    args = parser.parse_args(argv)
    if args.command == "seed":
        if not settings.use_database:
            sys.exit("DATABASE_URL is not configured")
        count = seed_employees_from_json(Path(args.file))
        print(f"Seeded {count} employees")


if __name__ == "__main__":
    main()
