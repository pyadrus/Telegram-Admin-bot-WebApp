import asyncio
import logging
import sys

from loguru import logger  # https://github.com/Delgan/loguru

from handlers.user_handlers.user_handlers import user_handlers  # Регистрация команд пользователя

# Импортируем обработчики команд
from handlers.admin_handlers.admin_help import register_help_handlers  # Регистрация команд администратора
from handlers.bot_handlers.bot_handlers import register_bot_handlers
from handlers.bot_handlers.messages_handlers import register_message_handlers

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
        # Регистрация обработчиков функций бота (удаление системных сообщений в группе)
        register_bot_handlers()
        # Удаление стикеров
        register_message_handlers()
        # Регистрация обработчиков пользовательских команд, таких как /start
        user_handlers()
        # Регистрация обработчиков административных команд, таких как /help
        register_help_handlers()
    except Exception as error:
        # Логирование исключений, если что-то пошло не так
        logger.exception(error)


# Точка входа в программу
if __name__ == "__main__":
    # Настройка базового логирования для вывода сообщений в консоль
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    # Запуск асинхронной главной функции
    asyncio.run(main())
