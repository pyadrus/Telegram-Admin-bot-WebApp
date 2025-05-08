import asyncio

from loguru import logger  # https://github.com/Delgan/loguru

from handlers.admin.group_restrictions import get_group_restrictions
from handlers.bot.bot import register_bot_handlers
from handlers.bot.messages import register_message_handlers
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
        logger.info("Бот watchman_admin_bot запущен")
        # Удаление ссылок и стикеров
        register_message_handlers()
        # Удаление системных сообщений об присоединении новых участников в группу Telegram
        register_bot_handlers()
        # Включение ограничений по группам
        get_group_restrictions()

        # Добавление обработчиков команд (добавление плохих слов в базу данных, выдача особенных привилегий пользователям и т.д.)
        # register_admin_handlers()

        await dp.start_polling(bot)

    except Exception as error:
        # Логирование исключений, если что-то пошло не так
        logger.exception(error)


# Точка входа в программу
if __name__ == "__main__":
    # Запуск асинхронной главной функции
    asyncio.run(main())
