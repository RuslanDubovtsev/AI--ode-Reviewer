"""
File reading module for AI Code Reviewer.
Handles file validation, reading, and path resolution.
"""

import os
from typing import List, Optional

from ai_code_reviewer.exceptions import FileReadError, FileTooLargeError

# Maximum file size in bytes (10 MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

# Directories to skip during recursive traversal
IGNORED_DIRS: set = {
    ".git", "__pycache__", "node_modules", "venv", ".venv",
    "env", ".idea", ".vscode", ".mypy_cache", ".pytest_cache",
}

# Files to skip explicitly by name
IGNORED_FILES: set = {
    ".DS_Store", "package-lock.json", "yarn.lock", ".env",
    "data.json", "poetry.lock",
}

# Allowed source code extensions
ALLOWED_EXTENSIONS: set = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".html", ".css", ".json",
    ".c", ".cpp", ".h", ".hpp", ".cs", ".java", ".go", ".rs", ".php",
    ".sh", ".md", ".yml", ".yaml", ".sql", ".rb", ".swift", ".kt",
    ".scala", ".xml", ".yaml", ".toml", ".ini", ".cfg",
}


def read_code_file(filepath: str) -> str:
    """
    Read the content of a source code file.

    Args:
        filepath: Path to the file to read.

    Returns:
        The file contents as a string.

    Raises:
        FileReadError: If the file does not exist, is not a file, or cannot be read.
        FileTooLargeError: If the file exceeds the maximum allowed size.
    """
    if not os.path.exists(filepath):
        raise FileReadError(f"Файл не найден по пути: {filepath}")

    if not os.path.isfile(filepath):
        raise FileReadError(f"Указанный путь не является файлом: {filepath}")

    file_size = os.path.getsize(filepath)
    if file_size > MAX_FILE_SIZE:
        size_mb = file_size / (1024 * 1024)
        raise FileTooLargeError(
            f"Файл слишком большой ({size_mb:.1f} МБ). "
            f"Максимальный размер: {MAX_FILE_SIZE // (1024 * 1024)} МБ."
        )

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        # Try a fallback encoding
        try:
            with open(filepath, "r", encoding="latin-1") as f:
                return f.read()
        except Exception as exc:
            raise FileReadError(
                f"Не удалось прочитать файл {filepath}: {exc}"
            ) from exc
    except IOError as exc:
        raise FileReadError(
            f"Ошибка ввода-вывода при чтении файла {filepath}: {exc}"
        ) from exc
    except Exception as exc:
        raise FileReadError(
            f"Неизвестная ошибка при чтении файла {filepath}: {exc}"
        ) from exc


def list_source_files(directory: str) -> List[str]:
    """
    Recursively find all supported source code files in a directory,
    skipping ignored directories and files.

    Args:
        directory: Path to the directory to scan.

    Returns:
        A sorted list of file paths matching supported extensions.

    Raises:
        FileReadError: If the directory does not exist.
    """
    if not os.path.isdir(directory):
        raise FileReadError(f"Директория не найдена: {directory}")

    files_to_review: List[str] = []
    for root, dirs, files in os.walk(directory):
        # Prune ignored directories in-place
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]  # Полное изменение списка

        for filename in files:
            if filename in IGNORED_FILES:
                continue
            _, ext = os.path.splitext(filename)
            if ext.lower() in ALLOWED_EXTENSIONS:
                files_to_review.append(os.path.join(root, filename))

    return sorted(files_to_review)
