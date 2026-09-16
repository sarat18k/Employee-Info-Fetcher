import uvicorn

from employee_info_fetcher.settings import get_settings


def serve() -> None:
    settings = get_settings()
    uvicorn.run(
        "employee_info_fetcher.api.app:create_app",
        factory=True,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    serve()
