import asyncio

from loguru import logger  # https://github.com/Delgan/loguru

from handlers.admin import register_admin_handlers
from handlers.start import register_start_handlers
from handlers.subscription import register_subscription_handlers
from handlers.bot import register_bot_handlers
from handlers.messages import register_message_handlers
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
        register_start_handlers()
        # Удаление ссылок и стикеров
        register_message_handlers()
        # Удаление системных сообщений об присоединении новых участников в группу Telegram
        register_bot_handlers()
        # Добавление обработчиков команд (добавление плохих слов в базу данных, выдача особенных привилегий пользователям и т.д.)
        register_admin_handlers()
        # Проверка на подписку
        register_subscription_handlers()

        await dp.start_polling(bot)

    except Exception as error:
        # Логирование исключений, если что-то пошло не так
        logger.exception(error)


# Точка входа в программу
if __name__ == "__main__":
    # Запуск асинхронной главной функции
    asyncio.run(main())
