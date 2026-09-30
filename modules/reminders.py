"""
Модуль напоминаний
==================
Создание и управление напоминаниями.
Бот пришлёт сообщение в указанное время.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

import config

logger = logging.getLogger(__name__)


def load_reminders() -> dict:
    """Загружает напоминания."""
    if config.REMINDERS_FILE.exists():
        with open(config.REMINDERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_reminders(reminders: dict):
    """Сохраняет напоминания."""
    with open(config.REMINDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(reminders, f, ensure_ascii=False, indent=2)


def add_reminder(text: str, time_str: str, user_id: str = "") -> str:
    """
    Добавляет напоминание.

    Args:
        text: Текст напоминания
        time_str: Время в формате "YYYY-MM-DD HH:MM" или "через N минут"
        user_id: ID пользователя

    Returns:
        Сообщение о результате
    """
    reminders = load_reminders()

    # Парсим время
    if time_str.startswith("через"):
        # Формат: "через 30 минут" или "через 1 час"
        parts = time_str.split()
        if len(parts) >= 3:
            amount = int(parts[1])
            unit = parts[2]
            if "минут" in unit:
                remind_time = datetime.now() + timedelta(minutes=amount)
            elif "час" in unit:
                remind_time = datetime.now() + timedelta(hours=amount)
            elif "дн" in unit:
                remind_time = datetime.now() + timedelta(days=amount)
            else:
                return "❌ Не понял время. Формат: /remind <текст> через 30 минут"
        else:
            return "❌ Формат: /remind <текст> через 30 минут"
    else:
        # Формат: "2024-12-25 14:30"
        try:
            remind_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
        except ValueError:
            return "❌ Формат времени: ГГГГ-ММ-ДД ЧЧ:ММ или \"через N минут\""

    reminder_id = f"rem_{len(reminders) + 1}"
    reminders[reminder_id] = {
        "text": text,
        "time": remind_time.isoformat(),
        "user_id": user_id,
        "created": datetime.now().isoformat(),
        "sent": False,
    }
    save_reminders(reminders)

    return (
        f"✅ Напоминание создано!\n"
        f"📝 {text}\n"
        f"⏰ {remind_time.strftime('%d.%m.%Y %H:%M')}"
    )


def list_reminders() -> str:
    """Список всех напоминаний."""
    reminders = load_reminders()
    if not reminders:
        return "⏰ Напоминаний пока нет.\nДобавь: /remind <текст> через 30 минут"

    text = "⏰ <b>Напоминания:</b>\n\n"
    for rid, data in reminders.items():
        status = "✅" if data.get("sent") else "⏳"
        time_str = datetime.fromisoformat(data["time"]).strftime("%d.%m %H:%M")
        text += f"{status} <code>{rid}</code> — {data['text'][:40]} ({time_str})\n"
    return text


def delete_reminder(reminder_id: str) -> str:
    """Удаляет напоминание."""
    reminders = load_reminders()
    if reminder_id in reminders:
        del reminders[reminder_id]
        save_reminders(reminders)
        return f"✅ Напоминание <code>{reminder_id}</code> удалено!"
    return f"❌ Напоминание <code>{reminder_id}</code> не найдено!"


def check_reminders() -> list:
    """
    Проверяет, какие напоминания пора отправить.

    Returns:
        Список напоминаний для отправки
    """
    reminders = load_reminders()
    now = datetime.now()
    due = []

    for rid, data in reminders.items():
        if not data.get("sent"):
            remind_time = datetime.fromisoformat(data["time"])
            if remind_time <= now:
                due.append((rid, data))

    return due


def mark_sent(reminder_id: str):
    """Отмечает напоминание как отправленное."""
    reminders = load_reminders()
    if reminder_id in reminders:
        reminders[reminder_id]["sent"] = True
        save_reminders(reminders)
