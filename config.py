"""
Конфигурация Userbot-Менеджера
==============================
Все настройки проекта в одном месте.
При деплое на Render/Railway переменные читаются из окружения.
"""

import os
from pathlib import Path

# ══════════════════════════════════════════════════════════════
#  ФУНКЦИЯ ЧТЕНИЯ ПЕРЕМЕННЫХ
# ══════════════════════════════════════════════════════════════

def get_env(key: str, default: str = "") -> str:
    """Читает переменную из окружения или возвращает значение по умолчанию."""
    return os.environ.get(key, default)

# ══════════════════════════════════════════════════════════════
#  TELEGRAM BOT (для управления)
# ══════════════════════════════════════════════════════════════

BOT_TOKEN = get_env("BOT_TOKEN", "8275482287:AAEO9YvDNd8Tc94UAthO7w8193ABog-Dc40")

# ID администратора (узнать через @userinfobot)
ADMIN_ID = get_env("ADMIN_ID", "")  # Вставь свой ID

# ══════════════════════════════════════════════════════════════
#  TELEGRAM USERBOT (для работы от твоего имени)
# ══════════════════════════════════════════════════════════════

# API ID и API Hash с https://my.telegram.org
API_ID = int(get_env("API_ID", "32146160"))
API_HASH = get_env("API_HASH", "ae96a4fa8b6c045b6c79c4f5b15ceb34")

# ══════════════════════════════════════════════════════════════
#  MISTRAL API (ИИ)
# ══════════════════════════════════════════════════════════════

# API-ключ Mistral (получи бесплатно на https://console.mistral.ai)
MISTRAL_API_KEY = get_env("MISTRAL_API_KEY", "mstrl_epddb9NmVsOkrxja0hZTZI0G7Z1llGqW_4nSAxD")

# Модель Mistral
MISTRAL_MODEL = get_env("MISTRAL_MODEL", "mistral-large-latest")

# ══════════════════════════════════════════════════════════════
#  НАСТРОЙКИ МОДУЛЕЙ
# ══════════════════════════════════════════════════════════════

# Автоответы
AUTO_REPLY_ENABLED = True
AUTO_REPLY_DELAY = 2  # Секунды перед ответом (чтобы не спамить)

# Рассылки
BROADCAST_DELAY = 0.5  # Задержка между сообщениями (секунды)
BROADCAST_CONFIRM = True  # Спрашивать подтверждение перед рассылкой

# Мониторинг
MONITOR_INTERVAL = 300  # Как часто проверять (секунды, по умолчанию 5 мин)

# Напоминания
REMINDER_CHECK_INTERVAL = 30  # Как часто проверять напоминания (секунды)

# ══════════════════════════════════════════════════════════════
#  ПУТИ
# ══════════════════════════════════════════════════════════════

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MODULES_DIR = BASE_DIR / "modules"

DATA_DIR.mkdir(exist_ok=True)
MODULES_DIR.mkdir(exist_ok=True)

# Файлы данных
HISTORY_FILE = DATA_DIR / "history.json"
CONTACTS_FILE = DATA_DIR / "contacts.json"
REMINDERS_FILE = DATA_DIR / "reminders.json"
MONITORS_FILE = DATA_DIR / "monitors.json"
AUTOREPLY_FILE = DATA_DIR / "autoreply.json"
BROADCAST_FILE = DATA_DIR / "broadcast.json"
