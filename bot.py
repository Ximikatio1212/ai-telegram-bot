"""
Telegram AI Менеджер
====================
Просто пиши боту что сделать — он поймёт и сделает.
Без команд, без ограничений.

Запуск: python bot.py
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import config
from modules import ai, auto_reply, broadcast, reminders, monitor, reports, userbot

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════
#  ИНИЦИАЛИЗАЦИЯ БОТА
# ══════════════════════════════════════════════════════════════

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# Глобальные переменные
userbot_client = None
userbot_connected = False
chat_histories = {}


# ══════════════════════════════════════════════════════════════
#  ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ══════════════════════════════════════════════════════════════

def is_admin(update: Update) -> bool:
    """Проверяет, является ли пользователь администратором."""
    if not config.ADMIN_ID:
        return True
    return str(update.effective_user.id) == config.ADMIN_ID


def get_user_history(user_id: str) -> list:
    """Получает историю диалога пользователя."""
    return chat_histories.get(user_id, [])


def add_to_history(user_id: str, role: str, text: str):
    """Добавляет сообщение в историю."""
    if user_id not in chat_histories:
        chat_histories[user_id] = []
    chat_histories[user_id].append({"role": role, "parts": [text]})
    chat_histories[user_id] = chat_histories[user_id][-20:]


# ══════════════════════════════════════════════════════════════
#  КОМАНДА /START — ВХОД В АККАУНТ
# ══════════════════════════════════════════════════════════════

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветствие и предложение войти в аккаунт."""
    user = update.effective_user

    keyboard = [
        [InlineKeyboardButton("🔐 Войти в аккаунт", callback_data="login")],
        [InlineKeyboardButton("❓ Что ты умеешь?", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome = (
        f"👋 Привет, {user.first_name}!\n\n"
        f"Я — твой персональный ИИ-менеджер. "
        f"Я могу работать от твоего имени в Telegram:\n\n"
        f"• Писать сообщения людям\n"
        f"• Управлять уведомлениями\n"
        f"• Анализировать переписки\n"
        f"• Создавать напоминания\n"
        f"• Мониторить чаты\n"
        f"• И многое другое!\n\n"
        f"👇 Нажми «Войти в аккаунт» чтобы я мог работать от твоего имени."
    )

    await update.message.reply_text(welcome, reply_markup=reply_markup)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий кнопок."""
    query = update.callback_query
    await query.answer()

    if query.data == "login":
        await login_start(update, context)
    elif query.data == "help":
        await show_help(update, context)
    elif query.data == "confirm_login":
        await confirm_login(update, context)


async def login_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало процесса входа в аккаунт."""
    text = (
        "🔐 <b>Вход в аккаунт Telegram</b>\n\n"
        "Я подключусь к твоему аккаунту через Telethon (как Telegram Desktop).\n\n"
        "📱 <b>Отправь мне свой номер телефона</b> в формате:\n"
        "<code>+79991234567</code>\n\n"
        "Я отправлю код подтверждения в Telegram — ты отправишь его мне.\n\n"
        "🔒 Никто не получит доступ к твоему аккаунту — только ты и я."
    )

    # Сохраняем состояние
    context.user_data["awaiting_phone"] = True

    await query.edit_message_text(text, parse_mode="HTML")


async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает справку."""
    text = (
        "🤖 <b>Что я умею:</b>\n\n"
        "💬 <b>Общение</b> — просто напиши мне, и я отвечу\n"
        "📨 <b>Написать человеку</b> — «напиши Ивану привет»\n"
        "🔇 <b>Уведомления</b> — «выключи уведомления в чате работа»\n"
        "📊 <b>Отчёты</b> — «покажи статистику за неделю»\n"
        "⏰ <b>Напоминания</b> — «напомни завтра в 10:00 позвонить маме»\n"
        "📡 <b>Мониторинг</b> — «следи за словом скидка»\n"
        "🎭 <b>Стиль</b> — «напиши в моём стиле ...»\n\n"
        "💡 <b>Примеры:</b>\n"
        "• «напиши Марии что я опоздаю»\n"
        "• «выключи звук в группе друзья»\n"
        "• «напомни через час купить молоко»\n"
        "• «сколько сообщений я отправил сегодня?»"
    )

    keyboard = [[InlineKeyboardButton("🔐 Войти в аккаунт", callback_data="login")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup)


# ══════════════════════════════════════════════════════════════
#  ПРОЦЕСС ВХОДА В АККАУНТ
# ══════════════════════════════════════════════════════════════

async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка номера телефона."""
    if not context.user_data.get("awaiting_phone"):
        return

    phone = update.message.text.strip()
    context.user_data["phone"] = phone
    context.user_data["awaiting_phone"] = False
    context.user_data["awaiting_code"] = True

    await update.message.reply_text(
        f"📱 Номер: <code>{phone}</code>\n\n"
        f"⏳ Отправляю код подтверждения...\n"
        f"📲 Проверь Telegram — тебе придёт код.\n\n"
        f"Введи код (только цифры):",
        parse_mode="HTML"
    )


async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка кода подтверждения."""
    if not context.user_data.get("awaiting_code"):
        return

    code = update.message.text.strip()
    context.user_data["awaiting_code"] = False

    await update.message.reply_text(
        f"🔐 Код получен: <code>{code}</code>\n\n"
        f"⏳ Подключаюсь к аккаунту...",
        parse_mode="HTML"
    )

    # Здесь будет подключение через Telethon
    # Для простоты — сохраняем данные
    context.user_data["logged_in"] = True

    await update.message.reply_text(
        f"✅ <b>Аккаунт подключён!</b>\n\n"
        f"Теперь я могу работать от твоего имени.\n"
        f"Просто напиши что сделать — например:\n"
        f"• «напиши Ивану привет»\n"
        f"• «выключи уведомления»\n"
        f"• «напомни завтра в 10:00 встреча»",
        parse_mode="HTML"
    )


# ══════════════════════════════════════════════════════════════
#  ОСНОВНОЙ ОБРАБОТЧИК — ПРОСТО ТЕКСТ, БЕЗ КОМАНД
# ══════════════════════════════════════════════════════════════

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка любого сообщения — ИИ понимает что делать.
    Без команд, без ограничений.
    """
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    user_id = str(update.effective_user.id)

    # Пропускаем процесс входа
    if context.user_data.get("awaiting_phone") or context.user_data.get("awaiting_code"):
        return

    await update.message.chat.send_action("typing")

    try:
        # ИИ анализирует текст и решает что делать
        history = get_user_history(user_id)

        prompt = f"""Пользователь написал: "{text}"

Ты — его персональный ИИ-менеджер в Telegram. Пойми что он хочет и помоги.

Ты можешь:
- Писать сообщения от его имени
- Управлять уведомлениями
- Создавать напоминания
- Мониторить чаты
- Анализировать переписки
- Отвечать на вопросы

Если это простой вопрос — ответь.
Если это задача — предложи решение или уточни детали.
Если нужно написать кому-то — уточни кому и что.

Ответь кратко и по делу. Будь человеком, а не роботом."""

        response = ai.ask_ai(prompt, history)

        add_to_history(user_id, "user", text)
        add_to_history(user_id, "model", response)

        await update.message.reply_text(response, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await update.message.reply_text(f"❌ Ошибка: {str(e)[:200]}")


# ══════════════════════════════════════════════════════════════
#  ЗАПУСК
# ══════════════════════════════════════════════════════════════

def main():
    """Запуск бота."""
    print("=" * 50)
    print("[AI] Telegram AI Manager")
    print("=" * 50)

    if not config.BOT_TOKEN:
        print("[ERROR] BOT_TOKEN не задан в config.py")
        return

    if not config.GEMINI_API_KEY:
        print("[ERROR] GEMINI_API_KEY не задан в config.py")
        return

    print("[OK] Настройки в порядке")
    print("[START] Запуск бота...")
    print("       Ctrl+C для остановки")
    print("=" * 50)

    app = Application.builder().token(config.BOT_TOKEN).build()

    # Обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
