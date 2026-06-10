import os
import sys

def read_code_file(filepath):
    """
    Reads the content of the specified file.
    Performs checks for file existence and supported extensions.
    """
    if not os.path.exists(filepath):
        print(f"Ошибка: Файл не найден по пути: {filepath}", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(filepath):
        print(f"Ошибка: Указанный путь не является файлом: {filepath}", file=sys.stderr)
        sys.exit(1)

    _, file_extension = os.path.splitext(filepath)
    supported_extensions = {".js", ".py", ".html", ".css"}

    if file_extension.lower() not in supported_extensions:
        print(f"Ошибка: Неподдерживаемое расширение файла {file_extension}. Поддерживаются: {", ".join(supported_extensions)}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"Ошибка при чтении файла {filepath}: {e}", file=sys.stderr)
        sys.exit(1)
