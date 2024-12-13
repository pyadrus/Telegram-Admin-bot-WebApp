import asyncio
import logging
import sys

from loguru import logger

# Импортируем обработчики команд
from handlers.admin_handlers.admin_help import register_help_handlers  # Регистрация команд администратора
from handlers.bot_handlers.bot_handlers import register_bot_handlers
from handlers.user_handlers.user_handlers import user_handlers  # Регистрация команд пользователя
from system.dispatcher import bot  # Экземпляр бота
from system.dispatcher import dp  # Диспетчер событий (Dispatcher)

# Настройка логирования: указываем файл, размер ротации и сжатие
logger.add("setting/log/log.log", rotation="1 MB", compression="zip")


async def main():
    """
    Главная асинхронная функция для запуска бота.
    Здесь инициализируются обработчики команд и запускается polling.
    """

    try:
        # Запуск диспетчера событий для обработки входящих сообщений
        await dp.start_polling(bot)
        # Регистрация обработчиков пользовательских команд, таких как /start
        user_handlers()
        # Регистрация обработчиков административных команд, таких как /help
        register_help_handlers()
        # Регистрация обработчиков функций бота
        register_bot_handlers()

    except Exception as error:
        # Логирование исключений, если что-то пошло не так
        logger.exception(error)


# Точка входа в программу
if __name__ == "__main__":
    # Настройка базового логирования для вывода сообщений в консоль
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    # Запуск асинхронной главной функции
    asyncio.run(main())
