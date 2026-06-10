# AI-Code-Reviewer

Консольный AI-помощник для ревью кода из файла или папки с файлами, который выводит результат в консоль или записывает в файл в удобочитаемом формате. Можно вписывать свои модели в рамках доступных API (OpenAI Compatible и Google Gemini)  
_Approved: Программа испытана на саму себя для рефакторинга_

## Скриншот

<img width="1376" height="71" alt="image" src="https://github.com/user-attachments/assets/db52e677-5d5c-493e-adb9-d95bcb0490ef" />
<img width="1417" height="500" alt="image" src="https://github.com/user-attachments/assets/bb23e327-06e5-4b73-b05f-d53b16da0c8a" />
<img width="1301" height="371" alt="image" src="https://github.com/user-attachments/assets/007d8e11-7688-4493-a3e9-672172a8d4e7" />

## Стек

- Python 3.12.5
- python-dotenv==1.2.2  
  requests==2.34.2
- DeepSeek API, Google AI API

## Как запустить локально

```
git clone https://github.com/RuslanDubovtsev/AI--ode-Reviewer.git
cd ThirdTask_AI_Assistant
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
<добавить файл/папку с фалйами для ревью>
python review.py <путь/к/файлу_или_папке> [--model <модель>] [--output <файл.md>]
```
## Деплой

Не требуется

## Что работает

1) Ревью файла  
2) Ревью каждого файла в папке (выполняется последовательно)  
3) Выбор модели, что соответствуют стандарту OpenAI Compatible или Google Gemini  
4) Запись результата в отдельный файл (.md, .txt или что-то еще)  

## Что не доделано
Все доделано

## Что я узнал во время работы

1) 
```
@dataclass(frozen=True)
class AppConfig:
    """Immutable application configuration."""
    api_key: str
    api_url: str
    model: str
    temperature: float = DEFAULT_TEMPERATURE
```  
Датакласс заместо словаря для типизации и неизменяемости  
2) Как работать с .env через библиотеку os и методом getenv  
3) load_dotenv() сохраняет все данные с .env в переменную окружения ОС, потом getenv достает их из этого системного словаря  
4)
```
for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
```
Изменение списка прям на ходу с помощью [:]  
5) Как обрабатывать массу ошибок
