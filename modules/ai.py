"""
Модуль ИИ (Google Gemini API)
=============================
Работа с искусственным интеллектом через Google Gemini API.
Бесплатный лимит: 1500 запросов в день.
"""

import logging
from typing import Optional

import google.generativeai as genai

import config

logger = logging.getLogger(__name__)

# Системный промпт бота-менеджера
SYSTEM_PROMPT = """Ты — персональный менеджер в Telegram. Твоя задача — помогать управлять задачами:

- Отвечать на вопросы кратко и по делу
- Помогать с рассылками, напоминаниями, мониторингом
- Быть вежливым, но эффективным
- Использовать эмодзи для красоты
- Если задача непонятна — уточни

Ты работаешь как "второй пользователь" аккаунта — помогаешь управлять делами.
"""

# Инициализация модели
genai.configure(api_key=config.GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name=config.GEMINI_MODEL,
    system_instruction=SYSTEM_PROMPT,
)


def ask_ai(prompt: str, history: Optional[list] = None) -> str:
    """
    Задать вопрос ИИ через Google Gemini API.

    Args:
        prompt: Вопрос или задача
        history: История диалога (список {"role": "user"/"model", "parts": [текст]})

    Returns:
        Ответ ИИ (строка)
    """
    try:
        if history:
            chat = model.start_chat(history=history)
            response = chat.send_message(prompt)
        else:
            response = model.generate_content(prompt)

        return response.text

    except Exception as e:
        logger.error(f"Ошибка Gemini: {e}")
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
