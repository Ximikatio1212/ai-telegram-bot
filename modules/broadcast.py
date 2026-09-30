"""
Модуль рассылок
===============
Массовая отправка сообщений пользователям.
ВАЖНО: Рассылка только с разрешения получателей!
"""

import json
import logging
import asyncio
from datetime import datetime
from pathlib import Path

import config

logger = logging.getLogger(__name__)


def load_broadcasts() -> dict:
    """Загружает данные рассылок."""
    if config.BROADCAST_FILE.exists():
        with open(config.BROADCAST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_broadcasts(data: dict):
    """Сохраняет данные рассылок."""
    with open(config.BROADCAST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_broadcast(name: str, message: str, targets: list) -> str:
    """
    Создаёт новую рассылку.

    Args:
        name: Название рассылки
        message: Текст сообщения
        targets: Список ID получателей

    Returns:
        Сообщение о результате
    """
    broadcasts = load_broadcasts()
    broadcasts[name] = {
        "message": message,
        "targets": targets,
        "created": datetime.now().isoformat(),
        "sent": False,
    }
    save_broadcasts(broadcasts)
    return (
        f"✅ Рассылка <b>{name}</b> создана!\n"
        f"📨 Получателей: {len(targets)}\n"
        f"💬 Текст: {message[:100]}"
    )


def list_broadcasts() -> str:
    """Список всех рассылок."""
    broadcasts = load_broadcasts()
    if not broadcasts:
        return "📨 Рассылок пока нет.\nСоздай: /bc_add <название> <текст>"

    text = "📨 <b>Рассылки:</b>\n\n"
    for name, data in broadcasts.items():
        status = "✅" if data.get("sent") else "⏳"
        text += f"{status} <b>{name}</b> — {len(data['targets'])} получ.\n"
    return text


async def execute_broadcast(name: str, bot) -> str:
    """
    Выполняет рассылку.

    Args:
        name: Название рассылки
        bot: Экземпляр бота

    Returns:
        Отчёт о результатах
    """
    broadcasts = load_broadcasts()
    if name not in broadcasts:
        return f"❌ Рассылка <b>{name}</b> не найдена!"

    bc = broadcasts[name]
    if bc.get("sent"):
        return f"⚠️ Рассылка <b>{name}</b> уже была отправлена!"

    sent = 0
    failed = 0

    for target in bc["targets"]:
        try:
            await bot.send_message(chat_id=target, text=bc["message"])
            sent += 1
            await asyncio.sleep(config.BROADCAST_DELAY)
        except Exception as e:
            logger.error(f"Ошибка отправки {target}: {e}")
            failed += 1

    bc["sent"] = True
    bc["sent_at"] = datetime.now().isoformat()
    bc["sent_count"] = sent
    bc["failed_count"] = failed
    save_broadcasts(broadcasts)

    return (
        f"📨 <b>Рассылка «{name}» завершена!</b>\n\n"
        f"✅ Отправлено: {sent}\n"
        f"❌ Ошибок: {failed}"
    )


def delete_broadcast(name: str) -> str:
    """Удаляет рассылку."""
    broadcasts = load_broadcasts()
    if name in broadcasts:
        del broadcasts[name]
        save_broadcasts(broadcasts)
        return f"✅ Рассылка <b>{name}</b> удалена!"
    return f"❌ Рассылка <b>{name}</b> не найдена!"
