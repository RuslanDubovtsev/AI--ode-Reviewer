"""
AI Code Reviewer — CLI tool for automated code review via AI APIs.

Usage:
    python review.py <path/to/file_or_folder> [--model <model>] [--output <file.md>]

Examples:
    python review.py my_script.py
    python review.py src/ --model deepseek-chat
    python review.py src/ --model gemini-2.5-flash --output review.md
"""

import os
import sys
from typing import List, Optional, Tuple

from ai_code_reviewer.config import get_config
from ai_code_reviewer.file_reader import read_code_file, list_source_files
from ai_code_reviewer.api_client import get_code_review
from ai_code_reviewer.exceptions import (
    CliUsageError,
    ConfigError,
    FileReadError,
    FileTooLargeError,
    ApiError,
    ApiTimeoutError,
    ApiConnectionError,
    ApiResponseError,
)


def parse_args(argv: List[str]) -> Tuple[str, str, Optional[str]]:
    """
    Parse command-line arguments using manual sys.argv parsing.

    Args:
        argv: The list of CLI arguments (excluding the program name).

    Returns:
        A tuple of (path, model_name, output_file).

    Raises:
        CliUsageError: If arguments are invalid or missing.
    """
    path: Optional[str] = None
    model: str = "deepseek-chat"
    output: Optional[str] = None

    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--model":
            if i + 1 >= len(argv):
                raise CliUsageError("Пропущено значение для флага --model.")
            model = argv[i + 1]
            i += 2
        elif arg == "--output":
            if i + 1 >= len(argv):
                raise CliUsageError("Пропущено значение для флага --output.")
            output = argv[i + 1]
            i += 2
        elif arg.startswith("-"):
            raise CliUsageError(f"Неизвестный флаг: {arg}")
        else:
            if path is None:
                path = arg
                i += 1
            else:
                raise CliUsageError(
                    f"Неизвестный или лишний позиционный аргумент: {arg}"
                )

    if path is None:
        raise CliUsageError(
            "Не указан путь к файлу или папке.\n"
            "Использование: python review.py <путь/к/файлу_или_папке> "
            "[--model <модель>] [--output <файл.md>]"
        )

    return path, model, output


def collect_files(path: str) -> List[str]:
    """
    Collect all files to review from the given path.

    Args:
        path: A file path or directory path.

    Returns:
        A list of file paths to review.

    Raises:
        FileReadError: If the path is invalid.
    """
    if os.path.isdir(path):
        files = list_source_files(path)
        if not files:
            raise FileReadError(
                f"В папке '{path}' не найдено поддерживаемых файлов для код-ревью."
            )
        return files
    else:
        return [path]


def build_markdown_report(
    reviews: List[Tuple[str, str]], path: str
) -> str:
    """
    Build a Markdown-formatted report from compiled reviews.

    Args:
        reviews: List of (filepath, review_text) tuples.
        path: The original path argument (for the report heading).

    Returns:
        A Markdown-formatted string.
    """
    if len(reviews) == 1:
        filepath, review_text = reviews[0]
        return f"# Код-ревью для {filepath}\n\n{review_text}\n"
    else:
        lines = [f"# Отчёт о код-ревью проекта: {path}\n"]
        for idx, (filepath, review_text) in enumerate(reviews, 1):
            lines.append(
                f"## [{idx}/{len(reviews)}] Файл: {filepath}\n\n"
                f"{review_text}\n\n---\n\n"
            )
        return "".join(lines)


def save_report(output_path: str, content: str) -> None:
    """
    Save the review report to a Markdown file.

    Args:
        output_path: Destination file path.
        content: Markdown content to write.

    Raises:
        FileReadError: If the file cannot be written.
    """
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Отчет успешно сохранен в файл: {output_path}")
    except OSError as exc:
        raise FileReadError(
            f"Ошибка при записи отчета в {output_path}: {exc}"
        ) from exc


def print_error(message: str) -> None:
    """Print an error message to stderr."""
    print(f"Ошибка: {message}", file=sys.stderr)


def main() -> None:
    """
    Main entry point for the AI Code Reviewer CLI.
    Parses arguments, collects files, sends them for review,
    and outputs or saves the results.
    """
    # --- Parse CLI arguments ---
    try:
        path, model, output = parse_args(sys.argv[1:])
    except CliUsageError as exc:
        print_error(str(exc))
        sys.exit(1)

    # --- Load configuration ---
    try:
        config = get_config(model)
    except ConfigError as exc:
        print_error(str(exc))
        sys.exit(1)

    # --- Collect files to review ---
    try:
        files_to_process = collect_files(path)
    except FileReadError as exc:
        print_error(str(exc))
        sys.exit(1)

    # --- Process each file ---
    total_files = len(files_to_process)
    compiled_reviews: List[Tuple[str, str]] = []

    for idx, filepath in enumerate(files_to_process, 1):
        print(f"\n[{idx}/{total_files}] Провожу код-ревью для файла: {filepath}...")

        # Read the file
        try:
            code_content = read_code_file(filepath)
        except FileTooLargeError as exc:
            print_error(str(exc))
            print("Пропускаю файл.", file=sys.stderr)
            continue
        except FileReadError as exc:
            print_error(str(exc))
            print("Пропускаю файл.", file=sys.stderr)
            continue

        # Get AI review
        try:
            review_result = get_code_review(code_content, config)
        except ApiTimeoutError as exc:
            print_error(str(exc))
            print("Пропускаю файл.", file=sys.stderr)
            continue
        except ApiConnectionError as exc:
            print_error(str(exc))
            print("Пропускаю файл.", file=sys.stderr)
            continue
        except ApiResponseError as exc:
            print_error(str(exc))
            print("Пропускаю файл.", file=sys.stderr)
            continue
        except ApiError as exc:
            print_error(str(exc))
            print("Пропускаю файл.", file=sys.stderr)
            continue

        # Print result to terminal
        print(f"\n### Результаты код-ревью для {filepath}:\n")
        print(review_result)
        print("\n" + "=" * 50 + "\n")

        compiled_reviews.append((filepath, review_result))

    # --- Save report to file if requested ---
    if output and compiled_reviews:
        try:
            markdown_content = build_markdown_report(compiled_reviews, path)
            save_report(output, markdown_content)
        except FileReadError as exc:
            print_error(str(exc))

    # Exit with non-zero code if no files were processed successfully
    if not compiled_reviews and files_to_process:
        print_error("Ни один файл не был успешно обработан.")
        sys.exit(1)


if __name__ == "__main__":
    main()
