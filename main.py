import asyncio
import logging
import sys

from loguru import logger  # https://github.com/Delgan/loguru

from handlers.bot_handlers.messages_handlers import register_message_handlers
# Импортируем обработчики команд
from handlers.user_handlers.user_handlers import user_handlers
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

        # Регистрация обработчиков пользовательских команд, таких как /start
        user_handlers()
        # Удаление ссылок и стикеров
        register_message_handlers()
        await dp.start_polling(bot)


    except Exception as error:
        # Логирование исключений, если что-то пошло не так
        logger.exception(error)


# Точка входа в программу
if __name__ == "__main__":
    # Настройка базового логирования для вывода сообщений в консоль
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    # Запуск асинхронной главной функции
    asyncio.run(main())
