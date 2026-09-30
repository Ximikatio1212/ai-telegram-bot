"""
Модуль ИИ (OpenRouter API)
==========================
Работа с искусственным интеллектом через OpenRouter API.
Бесплатный тариф: 20 запросов в минуту, много бесплатных моделей.
"""

import logging
from typing import Optional

import requests

import config

logger = logging.getLogger(__name__)

# Системный промпт бота-менеджер
SYSTEM_PROMPT = """Ты — персональный менеджер в Telegram. Твоя задача — помогать управлять задачами:

- Отвечать на вопросы кратко и по делу
- Помогать с рассылками, напоминаниями, мониторингом
- Быть вежливым, но эффективным
- Использовать эмодзи для красоты
- Если задача непонятна — уточни

Ты работаешь как "второй пользователь" аккаунта — помогаешь управлять делами.
"""

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


def ask_ai(prompt: str, history: Optional[list] = None) -> str:
    """
    Задать вопрос ИИ через OpenRouter API.

    Args:
        prompt: Вопрос или задача
        history: История диалога (список {"role": "user"/"assistant", "content": текст})

    Returns:
        Ответ ИИ (строка)
    """
    try:
        # Формируем сообщения
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Добавляем историю
        if history:
            for msg in history[-10:]:  # Последние 10 сообщений
                if msg.get("role") == "user":
                    messages.append({"role": "user", "content": msg["parts"][0]})
                elif msg.get("role") == "model":
                    messages.append({"role": "assistant", "content": msg["parts"][0]})

        # Добавляем текущий вопрос
        messages.append({"role": "user", "content": prompt})

        # Отправляем запрос
        response = requests.post(
            OPENROUTER_API_URL,
            headers={
                "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com",
                "X-Title": "AI Telegram Manager",
            },
            json={
                "model": config.OPENROUTER_MODEL,
                "messages": messages,
                "max_tokens": 1000,
                "temperature": 0.7,
            },
            timeout=30,
        )

        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        elif response.status_code == 429:
            return "❌ Лимит OpenRouter исчерпан. Подожди минуту."
        else:
            logger.error(f"Ошибка OpenRouter API: {response.status_code} - {response.text}")
            return f"❌ Ошибка ИИ: {response.status_code}"

    except requests.exceptions.Timeout:
        return "❌ ИИ не ответил вовремя. Попробуй ещё раз."
    except Exception as e:
        logger.error(f"Ошибка OpenRouter: {e}")
        return f"❌ Ошибка ИИ: {str(e)[:200]}"


def search_info(query: str) -> str:
    """Поиск информации через ИИ."""
    prompt = (
        f"Найди актуальную информацию по запросу: {query}\n"
        f"Дай краткий, но полезный ответ с фактами и источниками если возможно."
    )
    return ask_ai(prompt)


def generate_text(topic: str, style: str = "нейтральный") -> str:
    """Генерация текста по теме."""
    prompt = f"Напиши текст на тему: {topic}. Стиль: {style}. Будь краток и информативен."
    return ask_ai(prompt)


def analyze_text(text: str) -> str:
    """Анализ текста через ИИ."""
    prompt = f"Проанализируй следующий текст и дай краткое резюме:\n\n{text}"
    return ask_ai(prompt)
