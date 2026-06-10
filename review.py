import sys
import os

# Импортируем наши функциональные модули
from config import get_config
from file_reader import read_code_file
from api_client import get_code_review

def main():
    """
    Основная функция CLI-инструмента для код-ревью.
    """
    if len(sys.argv) < 2:
        print("Использование: python review.py <путь/к/файлу.js|py|html|css>", file=sys.stderr)
        sys.exit(1)

    filepath = sys.argv[1]

    # 1. Загрузка конфигурации (API-ключ)
    config = get_config()

    # 2. Чтение файла и валидация
    code_content = read_code_file(filepath)

    # 3. Отправка кода в DeepSeek API и получение ревью
    print(f"Провожу код-ревью для файла: {filepath}...")
    review_result = get_code_review(code_content, config)

    # 4. Вывод результата в терминал
    print("\n### Результаты код-ревью:\n")
    print(review_result)

if __name__ == "__main__":
    main()
