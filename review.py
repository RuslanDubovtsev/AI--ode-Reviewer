import sys
import os

# Импортируем наши функциональные модули
from ai_code_reviewer.config import get_config
from ai_code_reviewer.file_reader import read_code_file
from ai_code_reviewer.api_client import get_code_review

def list_files_in_directory(dir_path):
    """
    Рекурсивно находит все файлы исходного кода в папке,
    игнорируя системные каталоги и файлы зависимостей.
    """
    ignored_dirs = {'.git', '__pycache__', 'node_modules', 'venv', '.venv', 'env', '.idea', '.vscode'}
    ignored_files = {'.DS_Store', 'package-lock.json', 'yarn.lock', '.env', 'data.json'}
    allowed_extensions = {
        '.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.css', '.json',
        '.c', '.cpp', '.h', '.hpp', '.cs', '.java', '.go', '.rs', '.php',
        '.sh', '.md', '.yml', '.yaml', '.sql'
    }
    
    files_to_review = []
    for root, dirs, files in os.walk(dir_path):
        # Удаляем игнорируемые директории на месте, чтобы в них не заходить
        dirs[:] = [d for d in dirs if d not in ignored_dirs]
        for file in files:
            if file in ignored_files:
                continue
            _, ext = os.path.splitext(file)
            if ext.lower() in allowed_extensions:
                files_to_review.append(os.path.join(root, file))
    return sorted(files_to_review)

def main():
    """
    Основная функция CLI-инструмента для код-ревью.
    """
    args = sys.argv[1:]
    path = None
    model = "deepseek-chat"
    output = None
    
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--model":
            if i + 1 < len(args):
                model = args[i+1]
                i += 2
            else:
                print("Ошибка: пропущено значение для флага --model", file=sys.stderr)
                sys.exit(1)
        elif arg == "--output":
            if i + 1 < len(args):
                output = args[i+1]
                i += 2
            else:
                print("Ошибка: пропущено значение для флага --output", file=sys.stderr)
                sys.exit(1)
        elif arg.startswith("-"):
            print(f"Ошибка: Неизвестный флаг: {arg}", file=sys.stderr)
            sys.exit(1)
        else:
            if path is None:
                path = arg
                i += 1
            else:
                print(f"Ошибка: Неизвестный или лишний позиционный аргумент: {arg}", file=sys.stderr)
                sys.exit(1)
                
    if path is None:
        print("Использование: python review.py <путь/к/файлу_или_папке> [--model <модель>] [--output <файл.md>]", file=sys.stderr)
        sys.exit(1)

    # 1. Загрузка конфигурации (API-ключ и параметры)
    config = get_config(model)

    # 2. Сбор файлов для ревью
    if os.path.isdir(path):
        files_to_process = list_files_in_directory(path)
        if not files_to_process:
            print(f"В папке '{path}' не найдено поддерживаемых файлов для код-ревью.", file=sys.stderr)
            sys.exit(0)
    else:
        files_to_process = [path]

    # 3. Обработка каждого файла по-отдельности
    compiled_reviews = []
    total_files = len(files_to_process)
    
    for idx, filepath in enumerate(files_to_process, 1):
        print(f"\n[{idx}/{total_files}] Провожу код-ревью для файла: {filepath}...")
        
        # Чтение файла и валидация
        code_content = read_code_file(filepath)
        
        # Отправка кода по API и получение ревью
        review_result = get_code_review(code_content, config)
        
        # Вывод результата в терминал
        print(f"\n### Результаты код-ревью для {filepath}:\n")
        print(review_result)
        print("\n" + "="*50 + "\n")
        
        compiled_reviews.append((filepath, review_result))

    # 4. Сохранение в Markdown-файл
    if output:
        if len(compiled_reviews) == 1:
            filepath, review_result = compiled_reviews[0]
            markdown_content = f"# Код-ревью для {filepath}\n\n{review_result}\n"
        else:
            markdown_content = f"# Отчёт о код-ревью проекта: {path}\n\n"
            for idx, (filepath, review_result) in enumerate(compiled_reviews, 1):  # Для распаковки кортежа нужно указать две переменные внутри кортежа
                markdown_content += f"## [{idx}/{len(compiled_reviews)}] Файл: {filepath}\n\n{review_result}\n\n---\n\n"
        
        try:
            with open(output, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            print(f"Отчет успешно сохранен в файл: {output}")
        except Exception as e:
            print(f"Ошибка при записи отчета в {output}: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
