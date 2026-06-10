import os
import sys
from dotenv import load_dotenv

def get_config():
    """
    Loads configuration from environment variables or .env file.
    Returns a dictionary with API settings or exits if critical values are missing.
    """
    load_dotenv()
    
    api_key = os.getenv("deepseek_API")
    api_url = os.getenv("deepseek_url", "https://api.deepseek.com/v1")
    model = os.getenv("deepseek_chat", "deepseek-chat")
    
    if not api_key:
        print("Ошибка: API-ключ не найден.")
        print("Пожалуйста, добавьте deepseek_API='ваш_ключ' в файл .env или установите переменную окружения.")
        sys.exit(1)
        
    return {
        "api_key": api_key,
        "api_url": api_url.rstrip("/"),
        "model": model
    }
