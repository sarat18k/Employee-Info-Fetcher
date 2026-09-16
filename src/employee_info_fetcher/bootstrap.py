import os

from dotenv import load_dotenv

from employee_info_fetcher.logging_config import setup_logging
from employee_info_fetcher.settings import get_settings


def bootstrap() -> None:
    """Load environment, apply settings to process env, and configure logging."""
    load_dotenv()
    settings = get_settings()
    setup_logging(settings)

    if settings.openai_api_key:
        os.environ.setdefault(
            "OPENAI_API_KEY",
            settings.openai_api_key.get_secret_value(),
        )
    if settings.openai_model:
        os.environ.setdefault("OPENAI_MODEL_NAME", settings.openai_model)
