from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from messages.user_messages import user_info
from system.dispatcher import dp
from system.dispatcher import router
from loguru import logger


# Обработчик команды /start
@router.message(CommandStart())
async def user_start_handler(message: Message, state: FSMContext) -> None:
    """
    Обработчик команды /start
    :param message:
    :param state:
    :return:
    """
    try:
        await state.clear()  # Очистка предыдущих состояний

        user_id = message.from_user.id
        user_name = message.from_user.username or ""
        user_first_name = message.from_user.first_name or ""
        user_last_name = message.from_user.last_name or ""
        user_date = message.date.strftime("%Y-%m-%d %H:%M:%S")

        logger.info(f"User Info: {user_id}, {user_name}, {user_first_name}, {user_last_name}, {user_date}")

        await message.answer(user_info)

    except Exception as e:
        logger.error(f"Ошибка в обработчике /start: {e}")


def user_handlers():
    """Регистрируем handlers для всех пользователей"""
    dp.message.register(user_start_handler)
