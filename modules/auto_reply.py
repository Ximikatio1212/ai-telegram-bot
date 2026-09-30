"""
Модуль автоответов
==================
Автоматические ответы на входящие сообщения.
Можно настроить правила: если в сообщении есть слово X — ответить Y.
"""

import json
import logging
from pathlib import Path
from datetime import datetime

import config

logger = logging.getLogger(__name__)


def load_rules() -> dict:
    """Загружает правила автоответов."""
    if config.AUTOREPLY_FILE.exists():
        with open(config.AUTOREPLY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_rules(rules: dict):
    """Сохраняет правила автоответов."""
    with open(config.AUTOREPLY_FILE, "w", encoding="utf-8") as f:
        json.dump(rules, f, ensure_ascii=False, indent=2)


def add_rule(trigger: str, response: str) -> str:
    """
    Добавляет правило автоответа.

    Args:
        trigger: Слово-триггер (например: "привет")
        response: Текст ответа

    Returns:
        Сообщение о результате
    """
    rules = load_rules()
    rules[trigger.lower()] = {
        "response": response,
        "created": datetime.now().isoformat(),
        "enabled": True,
    }
    save_rules(rules)
    return f"✅ Правило добавлено:\n📝 Триггер: <code>{trigger}</code>\n💬 Ответ: {response}"


def remove_rule(trigger: str) -> str:
    """Удаляет правило автоответа."""
    rules = load_rules()
    trigger = trigger.lower()
    if trigger in rules:
        del rules[trigger]
        save_rules(rules)
        return f"✅ Правило <code>{trigger}</code> удалено!"
    return f"❌ Правило <code>{trigger}</code> не найдено!"


def list_rules() -> str:
    """Список всех правил автоответов."""
    rules = load_rules()
    if not rules:
        return "📋 Правил пока нет.\nДобавь: /ar_add <триггер> <ответ>"

    text = "📋 <b>Правила автоответов:</b>\n\n"
    for trigger, data in rules.items():
        status = "🟢" if data.get("enabled", True) else "🔴"
        text += f"{status} <code>{trigger}</code> → {data['response'][:50]}\n"
    return text


def check_auto_reply(text: str) -> str | None:
    """
    Проверяет, есть ли автоответ на сообщение.

    Args:
        text: Текст входящего сообщения

    Returns:
        Текст ответа или None
    """
    if not config.AUTO_REPLY_ENABLED:
        return None

    rules = load_rules()
    text_lower = text.lower()

    for trigger, data in rules.items():
        if data.get("enabled", True) and trigger in text_lower:
            return data["response"]

    return None


def toggle_rule(trigger: str) -> str:
    """Включает/выключает правило."""
    rules = load_rules()
    trigger = trigger.lower()
    if trigger in rules:
        rules[trigger]["enabled"] = not rules[trigger].get("enabled", True)
        save_rules(rules)
        status = "включено" if rules[trigger]["enabled"] else "выключено"
        return f"✅ Правило <code>{trigger}</code> {status}!"
    return f"❌ Правило <code>{trigger}</code> не найдено!"
