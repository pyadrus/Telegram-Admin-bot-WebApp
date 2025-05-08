from aiogram.filters import Command
from aiogram.types import ChatPermissions
from aiogram.types import Message

from system.dispatcher import router

# Только чтение (никто не может писать)
READ_ONLY = ChatPermissions(
    can_send_messages=False,
    can_send_media_messages=False,
    can_send_polls=False,
    can_send_other_messages=False,
    can_add_web_page_previews=False,
    can_change_info=False,
    can_invite_users=False,
    can_pin_messages=False,
)

# Полный доступ
FULL_ACCESS = ChatPermissions(
    can_send_messages=True,
    can_send_media_messages=True,
    can_send_polls=True,
    can_send_other_messages=True,
    can_add_web_page_previews=True,
    can_change_info=True,
    can_invite_users=True,
    can_pin_messages=True,
)


@router.message(Command("readonly"))
async def set_read_only(message: Message):
    """Метод set_chat_permissions позволяет боту устанавливать общие ограничения на действия всех участников группы , кроме администраторов."""
    chat_id = message.chat.id
    try:
        await message.bot.set_chat_permissions(chat_id=chat_id, permissions=READ_ONLY)
        await message.answer("Режим «только чтение» включен. Пользователи не могут отправлять сообщения.")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")


@router.message(Command("unrestrictchat"))
async def set_full_access(message: Message):
    """Метод set_chat_permissions позволяет боту устанавливать общие ограничения на действия всех участников группы , кроме администраторов.
    """
    chat_id = message.chat.id
    try:
        await message.bot.set_chat_permissions(chat_id=chat_id, permissions=FULL_ACCESS)
        await message.answer("Все участники теперь могут писать сообщения.")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")


def get_group_restrictions():
    router.message.register(set_read_only)
    router.message.register(set_full_access)
