import asyncio

from loguru import logger  # https://github.com/Delgan/loguru

from scr.bot.handlers.admin import register_send_id_handler
from scr.bot.system.dispatcher import bot, dp

# Настройка логирования: указываем файл, размер ротации и сжатие
logger.add("scr/setting/log/log.log", rotation="1 MB", compression="zip")


async def main():
    """
    Главная асинхронная функция для запуска бота.
    Здесь инициализируются обработчики команд и запускается polling.
    """
    try:
        logger.info("Бот запущен")
        register_send_id_handler()
        await dp.start_polling(bot)

    except Exception as error:
        # Логирование исключений, если что-то пошло не так
        logger.exception(error)


# Точка входа в программу
if __name__ == "__main__":
    # Запуск асинхронной главной функции
    asyncio.run(main())
