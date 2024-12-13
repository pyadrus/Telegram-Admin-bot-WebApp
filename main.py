import asyncio
import logging
import sys

from loguru import logger

from handlers.admin_handlers import admin_handlers
from system.dispatcher import bot
from system.dispatcher import dp

logger.add("setting/log/log.log", rotation="1 MB", compression="zip")


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
