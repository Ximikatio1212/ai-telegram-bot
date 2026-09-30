"""
Модуль мониторинга
==================
Слежение за событиями: новые сообщения, упоминания, ключевые слова.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

import config

logger = logging.getLogger(__name__)


def load_monitors() -> dict:
    """Загружает мониторы."""
    if config.MONITORS_FILE.exists():
        with open(config.MONITORS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_monitors(monitors: dict):
    """Сохраняет мониторы."""
    with open(config.MONITORS_FILE, "w", encoding="utf-8") as f:
        json.dump(monitors, f, ensure_ascii=False, indent=2)


def add_monitor(keyword: str, chat_id: int = None, notify: bool = True) -> str:
    """
    Добавляет монитор ключевого слова.

    Args:
        keyword: Слово для отслеживания
        chat_id: ID чата (None = все чаты)
        notify: Уведомлять при совпадении

    Returns:
        Результат
    """
    monitors = load_monitors()
    monitor_id = f"mon_{len(monitors) + 1}"
    monitors[monitor_id] = {
        "keyword": keyword.lower(),
        "chat_id": chat_id,
        "notify": notify,
        "created": datetime.now().isoformat(),
        "matches": 0,
    }
    save_monitors(monitors)
    return f"✅ Монитор добавлен!\n📝 Слово: <code>{keyword}</code>"


def list_monitors() -> str:
    """Список всех мониторов."""
    monitors = load_monitors()
    if not monitors:
        return "📡 Мониторов пока нет.\nДобавь: /mon_add <слово>"

    text = "📡 <b>Мониторы:</b>\n\n"
    for mid, data in monitors.items():
        status = "🟢" if data.get("enabled", True) else "🔴"
        text += f"{status} <code>{mid}</code> — {data['keyword']} ({data.get('matches', 0)} совп.)\n"
    return text


def delete_monitor(monitor_id: str) -> str:
    """Удаляет монитор."""
    monitors = load_monitors()
    if monitor_id in monitors:
        del monitors[monitor_id]
        save_monitors(monitors)
        return f"✅ Монитор <code>{monitor_id}</code> удалён!"
    return f"❌ Монитор <code>{monitor_id}</code> не найден!"


def check_monitors(text: str, chat_id: int = None) -> list:
    """
    Проверяет текст на совпадения с мониторами.

    Returns:
        Список совпадений [(monitor_id, keyword)]
    """
    monitors = load_monitors()
    text_lower = text.lower()
    matches = []

    for mid, data in monitors.items():
        if data.get("enabled", True):
            if data["keyword"] in text_lower:
                if data.get("chat_id") is None or data.get("chat_id") == chat_id:
                    matches.append((mid, data["keyword"]))
                    data["matches"] = data.get("matches", 0) + 1

    if matches:
        save_monitors(monitors)

    return matches


def toggle_monitor(monitor_id: str) -> str:
    """Включает/выключает монитор."""
    monitors = load_monitors()
    if monitor_id in monitors:
        monitors[monitor_id]["enabled"] = not monitors[monitor_id].get("enabled", True)
        save_monitors(monitors)
        status = "включён" if monitors[monitor_id]["enabled"] else "выключен"
        return f"✅ Монитор <code>{monitor_id}</code> {status}!"
    return f"❌ Монитор <code>{monitor_id}</code> не найден!"
