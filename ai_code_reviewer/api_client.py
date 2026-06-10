import json
import sys
import requests

def get_code_review(code_content, config):
    """
    Sends the code content to the DeepSeek API for review.
    Handles network and API errors.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config["api_key"]}"
    }

    # Более профессиональный и детальный промпт
    system_prompt = (
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

    user_prompt = f"""Проанализируй следующий код:
                    ```
                    {code_content}
                    ```
                    Предоставь подробный код-ревью."""

    data = {
        "model": config["model"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(
            f"{config["api_url"]}/chat/completions",
            headers=headers,
            data=json.dumps(data),
            timeout=310 
        )
        response.raise_for_status()  # Вызовет исключение для статусов 4xx/5xx
        
        response_json = response.json()
        if "choices" in response_json and len(response_json["choices"]) > 0:
            return response_json["choices"][0]["message"]["content"]
        else:
            print("Ошибка API: Неожиданный формат ответа от DeepSeek API.", file=sys.stderr)
            print(f"Полный ответ API: {response_json}", file=sys.stderr)
            sys.exit(1)
            
    except requests.exceptions.Timeout:
        print("Ошибка сети: Превышено время ожидания ответа от DeepSeek API.", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("Ошибка сети: Не удалось подключиться к DeepSeek API. Проверьте ваше интернет-соединение.", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"Ошибка HTTP: {e.response.status_code} - {e.response.reason}", file=sys.stderr)
        try:
            error_data = e.response.json()
            if "error" in error_data and "message" in error_data["error"]:
                print(f"Сообщение от API: {error_data["error"]["message"]}", file=sys.stderr)
        except json.JSONDecodeError:
            print("API вернул ошибку, но сообщение об ошибке не в формате JSON.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print("Ошибка: Не удалось декодировать JSON ответ от DeepSeek API.", file=sys.stderr)
        print(f"Сырой ответ API: {response.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Неизвестная ошибка при запросе к DeepSeek API: {e}", file=sys.stderr)
        sys.exit(1)
