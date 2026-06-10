"""
Configuration module for AI Code Reviewer.
Loads API keys and settings from environment variables / .env file.
Uses a dataclass for type-safe config instead of a plain dict.
"""

import os
from dataclasses import dataclass, field
from typing import Optional

from dotenv import load_dotenv

from ai_code_reviewer.exceptions import ConfigError


# Default values
DEFAULT_DEEPSEEK_URL = "https://api.deepseek.com/v1"
DEFAULT_GOOGLE_URL = "https://generativelanguage.googleapis.com/v1beta/models/"
DEFAULT_MODEL = "deepseek-chat"
DEFAULT_TEMPERATURE = 0.7


@dataclass(frozen=True)
class AppConfig:
    """Immutable application configuration."""
    api_key: str
    api_url: str
    model: str
    temperature: float = DEFAULT_TEMPERATURE


def _resolve_model_name(model_name: Optional[str] = None) -> str:
    """Resolve the model name, trying .env first, then fallback to default."""
    if model_name:
        return model_name
    env_model = os.getenv("DEFAULT_MODEL")
    return env_model or DEFAULT_MODEL


def get_config(model_name: Optional[str] = None) -> AppConfig:
    """
    Load configuration from environment variables or .env file.

    Args:
        model_name: Optional model name override. If None, determined from env or default.

    Returns:
        An AppConfig dataclass instance with validated settings.

    Raises:
        ConfigError: If a required API key is missing.
    """
    load_dotenv()
    model = _resolve_model_name(model_name)

    is_gemini = "gemini" in model.lower()

    if is_gemini:
        api_key = os.getenv("google_API")
        api_url = os.getenv("google_url", DEFAULT_GOOGLE_URL)
        if not api_key:
            raise ConfigError(
                "API-ключ google_API не найден в файле .env. "
                "Добавьте google_API=<ваш_ключ> в .env файл."
            )
    else:
        api_key = os.getenv("deepseek_API")
        api_url = os.getenv("deepseek_url", DEFAULT_DEEPSEEK_URL)
        if not api_key:
            raise ConfigError(
                "API-ключ deepseek_API не найден в файле .env. "
                "Добавьте deepseek_API=<ваш_ключ> в .env файл."
            )

    # Try to get temperature from env, fallback to default
    try:
        env_temp = os.getenv("TEMPERATURE")
        temperature = float(env_temp) if env_temp else DEFAULT_TEMPERATURE
    except (TypeError, ValueError):
        temperature = DEFAULT_TEMPERATURE

    return AppConfig(
        api_key=api_key,
        api_url=api_url.rstrip("/"),
        model=model,
        temperature=temperature,
    )
