"""
Модуль Userbot — работа от твоего имени
=======================================
Полный доступ к Telegram API от твоего аккаунта.
ИИ может делать ВСЁ, что может человек:
- Писать сообщения от твоего имени
- Читать переписки
- Управлять уведомлениями
- Вступать в группы
- И многое другое
"""

import json
import logging
from datetime import datetime
from pathlib import Path

import config

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════
#  РАБОТА С УВЕДОМЛЕНИЯМИ
# ══════════════════════════════════════════════════════════════

async def mute_all_notifications(client) -> str:
    """
    Выключает уведомления для всех чатов.

    Args:
        client: Экземпляр TelegramClient

    Returns:
        Результат операции
    """
    try:
        from telethon.tl.functions.account import UpdateNotifySettingsRequest
        from telethon.tl.types import InputNotifyPeer, InputPeerNotifySettings

        # Получаем все диалоги
        dialogs = await client.get_dialogs(limit=100)

        muted = 0
        for dialog in dialogs:
            try:
                await client(UpdateNotifySettingsRequest(
                    peer=InputNotifyPeer(dialog.entity),
                    settings=InputPeerNotifySettings(
                        mute_until=2**31 - 1,  # Бессрочно
                        show_previews=False,
                        silent=True,
                    )
                ))
                muted += 1
            except Exception as e:
                logger.error(f"Ошибка mute {dialog.name}: {e}")

        return f"🔇 Уведомления выключены для {muted} чатов!"

    except Exception as e:
        return f"❌ Ошибка: {str(e)[:200]}"


async def unmute_all_notifications(client) -> str:
    """Включает уведомления для всех чатов."""
    try:
        from telethon.tl.functions.account import UpdateNotifySettingsRequest
        from telethon.tl.types import InputNotifyPeer, InputPeerNotifySettings

        dialogs = await client.get_dialogs(limit=100)

        unmuted = 0
        for dialog in dialogs:
            try:
                await client(UpdateNotifySettingsRequest(
                    peer=InputNotifyPeer(dialog.entity),
                    settings=InputPeerNotifySettings(
                        mute_until=0,
                        show_previews=True,
                        silent=False,
                    )
                ))
                unmuted += 1
            except Exception as e:
                logger.error(f"Ошибка unmute {dialog.name}: {e}")

        return f"🔔 Уведомления включены для {unmuted} чатов!"

    except Exception as e:
        return f"❌ Ошибка: {str(e)[:200]}"


async def mute_chat(client, chat_id: int) -> str:
    """Выключает уведомления для конкретного чата."""
    try:
        from telethon.tl.functions.account import UpdateNotifySettingsRequest
        from telethon.tl.types import InputNotifyPeer, InputPeerNotifySettings

        entity = await client.get_entity(chat_id)
        await client(UpdateNotifySettingsRequest(
            peer=InputNotifyPeer(entity),
            settings=InputPeerNotifySettings(
                mute_until=2**31 - 1,
                show_previews=False,
                silent=True,
            )
        ))
        return f"🔇 Уведомления выключены для {entity.title if hasattr(entity, 'title') else chat_id}!"
    except Exception as e:
        return f"❌ Ошибка: {str(e)[:200]}"


# ══════════════════════════════════════════════════════════════
#  ОТПРАВКА СООБЩЕНИЙ ОТ ТВОЕГО ИМЕНИ
# ══════════════════════════════════════════════════════════════

async def send_as_user(client, chat_id: int, text: str) -> str:
    """
    Отправляет сообщение от твоего имени.

    Args:
        client: Экземпляр TelegramClient
        chat_id: ID чата или username
        text: Текст сообщения

    Returns:
        Результат операции
    """
    try:
        await client.send_message(chat_id, text)
        return f"✅ Сообщение отправлено в {chat_id}"
    except Exception as e:
        return f"❌ Ошибка: {str(e)[:200]}"


async def reply_to_message(client, chat_id: int, message_id: int, text: str) -> str:
    """Отвечает на конкретное сообщение от твоего имени."""
    try:
        await client.send_message(chat_id, text, reply_to=message_id)
        return f"✅ Ответ отправлен в {chat_id}"
    except Exception as e:
        return f"❌ Ошибка: {str(e)[:200]}"


async def forward_message(client, from_chat: int, to_chat: int, message_id: int) -> str:
    """Пересылает сообщение от твоего имени."""
    try:
        await client.forward_messages(to_chat, message_id, from_chat)
        return f"✅ Сообщение переслано в {to_chat}"
    except Exception as e:
        return f"❌ Ошибка: {str(e)[:200]}"


# ══════════════════════════════════════════════════════════════
#  ЧТЕНИЕ ПЕРЕПИСОК
# ══════════════════════════════════════════════════════════════

async def get_chat_history(client, chat_id: int, limit: int = 50) -> str:
    """
    Читает историю переписки.

    Args:
        client: Экземпляр TelegramClient
        chat_id: ID чата
        limit: Количество сообщений

    Returns:
        Форматированная история
    """
    try:
        messages = await client.get_messages(chat_id, limit=limit)
        text = f"📜 <b>История переписки ({len(messages)} сообщений):</b>\n\n"

        for msg in reversed(messages):
            sender = msg.sender.first_name if msg.sender else "?"
            text += f"💬 <b>{sender}:</b> {msg.text[:100] if msg.text else '[медиа]'}\n"

        return text
    except Exception as e:
        return f"❌ Ошибка: {str(e)[:200]}"


async def get_all_chats(client, limit: int = 100) -> str:
    """Получает список всех чатов."""
    try:
        dialogs = await client.get_dialogs(limit=limit)
        text = f"💬 <b>Чаты ({len(dialogs)}):</b>\n\n"

        for dialog in dialogs:
            name = dialog.name or "Без названия"
            text += f"📌 {name} (ID: {dialog.id})\n"

        return text
    except Exception as e:
        return f"❌ Ошибка: {str(e)[:200]}"


# ══════════════════════════════════════════════════════════════
#  АНАЛИЗ СТИЛЯ ОБЩЕНИЯ
# ══════════════════════════════════════════════════════════════

def load_style_profile() -> dict:
    """Загружает профиль стиля общения."""
    style_file = config.DATA_DIR / "style_profile.json"
    if style_file.exists():
        with open(style_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_style_profile(profile: dict):
    """Сохраняет профиль стиля общения."""
    style_file = config.DATA_DIR / "style_profile.json"
    with open(style_file, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)


async def analyze_chat_style(client, chat_id: int, limit: int = 100) -> str:
    """
    Анализирует твой стиль общения в чате.

    Args:
        client: Экземпляр TelegramClient
        chat_id: ID чата
        limit: Количество сообщений для анализа

    Returns:
        Описание стиля
    """
    try:
        me = await client.get_me()
        messages = await client.get_messages(chat_id, limit=limit)

        # Собираем только твои сообщения
        my_messages = []
        for msg in messages:
            if msg.sender and msg.sender.id == me.id and msg.text:
                my_messages.append(msg.text)

        if not my_messages:
            return "❌ Не найдено твоих сообщений в этом чате."

        # Сохраняем для анализа
        profile = load_style_profile()
        profile["messages"] = my_messages
        profile["analyzed_at"] = datetime.now().isoformat()
        save_style_profile(profile)

        # Анализируем через ИИ
        from modules import ai
        messages_text = chr(10).join(my_messages[:30])
        analysis_prompt = f"""Проанализируй стиль общения этого человека по его сообщениям:

{messages_text}

Опиши:
1. Тон общения (формальный/неформальный/дружелюбный)
2. Использование эмодзи
3. Длина сообщений
4. Особенности речи
5. Как он здоровается и прощается

Дай краткий профиль стиля."""

        style_analysis = ai.ask_ai(analysis_prompt)

        return f"🎭 <b>Анализ стиля общения:</b>\n\n{style_analysis}"

    except Exception as e:
        return f"❌ Ошибка: {str(e)[:200]}"


async def generate_in_style(client, context: str) -> str:
    """
    Генерирует сообщение в твоём стиле.

    Args:
        client: Экземпляр TelegramClient
        context: Контекст (кому, зачем)

    Returns:
        Сгенерированное сообщение
    """
    profile = load_style_profile()
    messages = profile.get("messages", [])

    if not messages:
        return "❌ Сначала проанализируй стиль: /style_analyze <chat_id>"

    from modules import ai
    prompt = f"""Напиши сообщение в стиле этого человека.

Примеры его сообщений:
{chr(10).join(messages[:10])}

Контекст: {context}

Напиши сообщение в его стиле — так, как написал бы он сам."""

    return ai.ask_ai(prompt)


# ══════════════════════════════════════════════════════════════
#  УПРАВЛЕНИЕ ЧАТАМИ
# ══════════════════════════════════════════════════════════════

async def join_chat(client, invite_link: str) -> str:
    """Вступает в чат по ссылке."""
    try:
        from telethon.tl.functions.messages import ImportChatInviteRequest
        result = await client(ImportChatInviteRequest(invite_link))
        return f"✅ Вступил в чат: {result.chats[0].title}"
    except Exception as e:
        return f"❌ Ошибка: {str(e)[:200]}"


async def leave_chat(client, chat_id: int) -> str:
    """Выходит из чата."""
    try:
        from telethon.tl.functions.channels import LeaveChannelRequest
        await client(LeaveChannelRequest(chat_id))
        return f"✅ Вышел из чата {chat_id}"
    except Exception as e:
        return f"❌ Ошибка: {str(e)[:200]}"


async def delete_message(client, chat_id: int, message_id: int) -> str:
    """Удаляет сообщение."""
    try:
        await client.delete_messages(chat_id, message_id)
        return f"✅ Сообщение удалено"
    except Exception as e:
        return f"❌ Ошибка: {str(e)[:200]}"


async def edit_message(client, chat_id: int, message_id: int, new_text: str) -> str:
    """Редактирует сообщение."""
    try:
        await client.edit_message(chat_id, message_id, new_text)
        return f"✅ Сообщение отредактировано"
    except Exception as e:
        return f"❌ Ошибка: {str(e)[:200]}"


# ══════════════════════════════════════════════════════════════
#  ПОИСК И НАВИГАЦИЯ
# ══════════════════════════════════════════════════════════════

async def search_messages(client, query: str, limit: int = 20) -> str:
    """Ищет сообщения по всем чатам."""
    try:
        result = await client.search_messages(query, limit=limit)
        text = f"🔍 <b>Результаты поиска ({len(result)}):</b>\n\n"

        for msg in result:
            chat = await msg.get_chat()
            chat_name = chat.title if hasattr(chat, 'title') else "?"
            text += f"💬 <b>{chat_name}:</b> {msg.text[:80] if msg.text else '[медиа]'}\n"

        return text
    except Exception as e:
        return f"❌ Ошибка: {str(e)[:200]}"


async def get_user_info(client, user_id: int) -> str:
    """Получает информацию о пользователе."""
    try:
        user = await client.get_entity(user_id)
        text = (
            f"👤 <b>Информация о пользователе:</b>\n\n"
            f"🆔 ID: <code>{user.id}</code>\n"
            f"📛 Имя: {user.first_name or ''}\n"
            f"📛 Фамилия: {user.last_name or ''}\n"
            f"📱 Username: @{user.username}\n" if user.username else ""
        )
        return text
    except Exception as e:
        return f"❌ Ошибка: {str(e)[:200]}"
