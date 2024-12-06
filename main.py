import asyncio
import logging
import sys

from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from loguru import logger

from handlers.admin_handlers import admin_handlers
from system.dispatcher import bot
from system.dispatcher import dp

logger.add("setting/log/log.log", rotation="1 MB", compression="zip")


class GetCountMembers(StatesGroup):
    """Создайте состояние, чтобы получить количество членов группы"""
    get_count_members_grup = State()


@dp.message_handler(commands=['count'])
async def get_count_members(message: types.Message):
    await message.answer(text='Enter the group ID for tracking')
    await GetCountMembers.get_count_members_grup.set()


@dp.message_handler(state=GetCountMembers.get_count_members_grup)
async def get_count_members_state(message: types.Message, state: FSMContext):
    """Получить количество участников в указанной группе"""
    chat_id = int(message.text)
    # Получить количество участников в группе
    count = await bot.get_chat_members_count(chat_id)
    # Ответить с помощью счетчика
    await message.answer(f'The number of members in the group is: {count}')
    # Сброс состояния
    await state.finish()


async def main():
    """Запуск бота"""
    try:
        admin_handlers()  # Регистрация обработчиков для администратора и пользователей
        await dp.start_polling(bot)
    except Exception as error:
        logger.exception(error)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
