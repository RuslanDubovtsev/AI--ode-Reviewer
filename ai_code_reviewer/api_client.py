"""
API client module for AI Code Reviewer.
Handles communication with DeepSeek and Google Gemini APIs.
"""

import json
from typing import Any, Dict

import requests

from ai_code_reviewer.config import AppConfig
from ai_code_reviewer.exceptions import (
    ApiConnectionError,
    ApiError,
    ApiResponseError,
    ApiTimeoutError,
)


# Request timeout in seconds
REQUEST_TIMEOUT = 310

# System prompt for code review
SYSTEM_PROMPT = (
    "Ты опытный старший инженер-программист, специализирующийся на глубоком "
    "анализе кода. Твоя задача — провести всесторонний код-ревью предоставленного кода. "
    "Оцени код по следующим критериям: потенциальные баги, уязвимости безопасности, "
    "оптимизация производительности, читаемость, поддерживаемость, соответствие "
    "лучшим практикам и паттернам проектирования. "
    "Предложи конкретные улучшения, рефакторинги и альтернативные подходы, "
    "аргументируя каждое предложение. Сосредоточься на деталях, но также "
    "предоставь высокоуровневую оценку архитектуры, если применимо. "
    "Особое внимание удели обработке ошибок, управлению ресурсами и "
    "масштабируемости."
)


def _build_user_prompt(code_content: str) -> str:
    """Build the user prompt with the code to review."""
    return (
        f"Проанализируй следующий код:\n```\n{code_content}\n```\n"
        "Предоставь подробный код-ревью."
    )


def _build_deepseek_payload(config: AppConfig, user_prompt: str) -> Dict[str, Any]:
    """Build the request payload for DeepSeek (OpenAI-compatible) API."""
    return {
        "model": config.model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": config.temperature,
    }


def _build_gemini_payload(config: AppConfig, user_prompt: str) -> Dict[str, Any]:
    """Build the request payload for Google Gemini API."""
    return {
        "contents": [
            {"role": "user", "parts": [{"text": user_prompt}]}
        ],
        "system_instruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "generationConfig": {
            "temperature": config.temperature,
        },
    }


def _call_deepseek_api(config: AppConfig, user_prompt: str) -> str:
    """
    Send a request to the DeepSeek (OpenAI-compatible) API.

    Args:
        config: Application configuration with API key, URL, and model.
        user_prompt: The prompt with code content to review.

    Returns:
        The review text from the API.

    Raises:
        ApiError: On any API or network failure.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.api_key}",
    }

    payload = _build_deepseek_payload(config, user_prompt)
    api_url = f"{config.api_url}/chat/completions"

    try:
        response = requests.post(
            api_url,
            headers=headers,
            data=json.dumps(payload),
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        response_json: Dict[str, Any] = response.json()

        choices = response_json.get("choices", [])
        if not choices:
            raise ApiResponseError(
                "Неожиданный формат ответа от DeepSeek API: отсутствуют choices.",
                raw_response=response_json,
            )

        return choices[0]["message"]["content"]

    except requests.exceptions.Timeout as exc:
        raise ApiTimeoutError(
            "Превышено время ожидания от DeepSeek API."
        ) from exc
    except requests.exceptions.ConnectionError as exc:
        raise ApiConnectionError(
            "Не удалось подключиться к DeepSeek API. Проверьте интернет-соединение."
        ) from exc
    except requests.exceptions.HTTPError as exc:
        _handle_http_error(exc, "DeepSeek")
    except json.JSONDecodeError as exc:
        raise ApiResponseError(
            "Не удалось декодировать JSON ответ от DeepSeek API.",
            raw_text=response.text if 'response' in locals() else None,
        ) from exc


def _call_gemini_api(config: AppConfig, user_prompt: str) -> str:
    """
    Send a request to the Google Gemini API.

    Args:
        config: Application configuration with API key, URL, and model.
        user_prompt: The prompt with code content to review.

    Returns:
        The review text from the API.

    Raises:
        ApiError: On any API or network failure.
    """
    headers = {
        "Content-Type": "application/json",
    }

    payload = _build_gemini_payload(config, user_prompt)

    # Ensure trailing slash for URL resolution
    api_url = config.api_url
    if not api_url.endswith("/"):
        api_url += "/"

    # Gemini passes API key as a query parameter
    url = f"{api_url}{config.model}:generateContent?key={config.api_key}"

    try:
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(payload),
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        response_json: Dict[str, Any] = response.json()

        candidates = response_json.get("candidates", [])
        if not candidates:
            raise ApiResponseError(
                "Неожиданный формат ответа от Gemini API: отсутствуют candidates.",
                raw_response=response_json,
            )

        # Gemini returns parts within content
        parts = candidates[0]["content"]["parts"]
        return "".join(part["text"] for part in parts)

    except requests.exceptions.Timeout as exc:
        raise ApiTimeoutError(
            "Превышено время ожидания от Gemini API."
        ) from exc
    except requests.exceptions.ConnectionError as exc:
        raise ApiConnectionError(
            "Не удалось подключиться к Gemini API. Проверьте интернет-соединение."
        ) from exc
    except requests.exceptions.HTTPError as exc:
        _handle_http_error(exc, "Gemini")
    except json.JSONDecodeError as exc:
        raise ApiResponseError(
            "Не удалось декодировать JSON ответ от Gemini API.",
            raw_text=response.text if 'response' in locals() else None,
        ) from exc


def _handle_http_error(exc: requests.exceptions.HTTPError, provider: str) -> None:
    """
    Handle HTTP errors from API responses with detailed error messages.

    Args:
        exc: The HTTPError exception.
        provider: The API provider name (for error messages).

    Raises:
        ApiResponseError: Always raises with formatted error details.
    """
    status_code = exc.response.status_code
    reason = exc.response.reason
    message = f"Ошибка HTTP {status_code} от {provider} API: {reason}"

    try:
        error_data = exc.response.json()
        if "error" in error_data:
            error_msg = error_data["error"].get("message", "")
            if error_msg:
                message += f" — {error_msg}"
        raise ApiResponseError(message, raw_response=error_data)
    except json.JSONDecodeError:
        raise ApiResponseError(
            message + " (тело ответа не в формате JSON).",
            raw_text=exc.response.text,
        )


def get_code_review(code_content: str, config: AppConfig) -> str:
    """
    Send the code content to the AI API for review.

    Args:
        code_content: The source code to review.
        config: Application configuration (API keys, model, etc.).

    Returns:
        The review text from the AI model.

    Raises:
        ApiError: On any API or network failure.
    """
    user_prompt = _build_user_prompt(code_content)
    is_gemini = "gemini" in config.model.lower()

    if is_gemini:
        return _call_gemini_api(config, user_prompt)
    else:
        return _call_deepseek_api(config, user_prompt)
