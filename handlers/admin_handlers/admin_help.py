from aiogram.filters import Command
from aiogram.types import Message

from messages.user_messages import info
from system.dispatcher import router, dp


@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    await message.answer(info, parse_mode="HTML")


def register_help_handlers():
    """Регистрация обработчиков для бота"""
    dp.message.register(help_handler)


if __name__ == '__main__':
    register_help_handlers()