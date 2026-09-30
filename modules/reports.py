"""
Модуль отчётов
==============
Генерация сводок и отчётов по активности.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

import config

logger = logging.getLogger(__name__)


async def generate_activity_report(client, days: int = 7) -> str:
    """
    Генерирует отчёт об активности за период.

    Args:
        client: Экземпляр TelegramClient
        days: Количество дней

    Returns:
        Текст отчёта
    """
    try:
        since = datetime.now() - timedelta(days=days)
        dialogs = await client.get_dialogs(limit=100)

        total_messages = 0
        active_chats = []

        for dialog in dialogs:
            try:
                messages = await client.get_messages(dialog.id, limit=50)
                recent = [m for m in messages if m.date and m.date > since]
                if recent:
                    active_chats.append({
                        "name": dialog.name or "Без названия",
                        "count": len(recent),
                    })
                    total_messages += len(recent)
            except:
                continue

        # Сортируем по активности
        active_chats.sort(key=lambda x: x["count"], reverse=True)

        text = f"📊 <b>Отчёт об активности за {days} дней:</b>\n\n"
        text += f"💬 Всего сообщений: {total_messages}\n"
        text += f"📌 Активных чатов: {len(active_chats)}\n\n"

        if active_chats:
            text += "<b>Топ чатов:</b>\n"
            for i, chat in enumerate(active_chats[:10], 1):
                text += f"  {i}. {chat['name']} — {chat['count']} сообщ.\n"

        return text

    except Exception as e:
        return f"❌ Ошибка: {str(e)[:200]}"


async def generate_chat_report(client, chat_id: int, days: int = 7) -> str:
    """
    Генерирует отчёт по конкретному чату.

    Args:
        client: Экземпляр TelegramClient
        chat_id: ID чата
        days: Количество дней

    Returns:
        Текст отчёта
    """
    try:
        since = datetime.now() - timedelta(days=days)
        messages = await client.get_messages(chat_id, limit=200)
        recent = [m for m in messages if m.date and m.date > since]

        # Считаем статистику
        senders = {}
        for msg in recent:
            sender = msg.sender.first_name if msg.sender else "?"
            senders[sender] = senders.get(sender, 0) + 1

        chat = await client.get_chat(chat_id)
        chat_name = chat.title if hasattr(chat, 'title') else "Чат"

        text = f"📊 <b>Отчёт по чату «{chat_name}»:</b>\n\n"
        text += f"📅 Период: {days} дней\n"
        text += f"💬 Сообщений: {len(recent)}\n\n"

        if senders:
            text += "<b>Участники:</b>\n"
            for sender, count in sorted(senders.items(), key=lambda x: x[1], reverse=True):
                text += f"  • {sender}: {count} сообщ.\n"

        return text

    except Exception as e:
        return f"❌ Ошибка: {str(e)[:200]}"


async def generate_daily_summary(client) -> str:
    """
    Генерирует ежедневную сводку.

    Returns:
        Текст сводки
    """
    try:
        since = datetime.now() - timedelta(days=1)
        dialogs = await client.get_dialogs(limit=50)

        summary = "📅 <b>Ежедневная сводка:</b>\n\n"

        for dialog in dialogs:
            try:
                messages = await client.get_messages(dialog.id, limit=20)
                recent = [m for m in messages if m.date and m.date > since]
                if recent:
                    summary += f"💬 <b>{dialog.name or 'Чат'}:</b> {len(recent)} сообщ.\n"
            except:
                continue

        return summary

    except Exception as e:
        return f"❌ Ошибка: {str(e)[:200]}"
