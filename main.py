import asyncio
import logging
import sys

from loguru import logger  # https://github.com/Delgan/loguru

from handlers.admin_handlers.admin_handlers import register_admin_handlers
from handlers.admin_handlers.count_handlers import regis_count_members
from handlers.bot_handlers.bot_handlers import register_bot_handlers
from handlers.bot_handlers.messages_handlers import register_message_handlers
# Импортируем обработчики команд
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
        # Удаление ссылок и стикеров
        register_message_handlers()
        # Удаление системных сообщений об присоединении новых участников в группу Telegram
        register_bot_handlers()
        # Добавление обработчиков команд (добавление плохих слов в базу данных, выдача особенных привилегий пользователям и т.д.)
        register_admin_handlers()

        regis_count_members()

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
