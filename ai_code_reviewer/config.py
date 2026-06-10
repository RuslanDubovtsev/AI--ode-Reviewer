import os
import sys
from dotenv import load_dotenv

def get_config(model_name="deepseek-chat"):
    """
    Loads configuration from environment variables or .env file.
    Returns a dictionary with API settings or exits if critical values are missing.
    """
    load_dotenv()  # Перевод данных из .env в переменную окружения ОС в виде пары ключ-значение
    
    # Проверяем наличие указанной модели в значениях переменных окружения
    model_exists = any(val == model_name for val in os.environ.values())
    if not model_exists:
        print(f"Ошибка: Модель '{model_name}' не найдена в файле .env.", file=sys.stderr)
        sys.exit(1)
        
    if "gemini" in model_name.lower():
        api_key = os.getenv("google_API")
        api_url = os.getenv("google_url", "https://generativelanguage.googleapis.com/v1beta/openai/")
        if not api_key:
            print("Ошибка: API-ключ google_API не найден в файле .env.", file=sys.stderr)
            sys.exit(1)
    else:
        api_key = os.getenv("deepseek_API")
        api_url = os.getenv("deepseek_url", "https://api.deepseek.com/v1")
        if not api_key:
            print("Ошибка: API-ключ deepseek_API не найден в файле .env.", file=sys.stderr)
            sys.exit(1)
    
    return {
        "api_key": api_key,
        "api_url": api_url.rstrip("/"),
        "model": model_name
    }
