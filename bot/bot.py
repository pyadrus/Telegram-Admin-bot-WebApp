import asyncio

from loguru import logger  # https://github.com/Delgan/loguru

from handlers.member import (handle_new_member, handle_member_left,
                             delete_system_message_new_member, delete_system_message_member_left)
from handlers.subscription import check_subscription, on_chat_member_update
# Импортируем обработчики команд
from system.dispatcher import bot, router  # Экземпляр бота
from system.dispatcher import dp  # Диспетчер событий (Dispatcher)

# Настройка логирования: указываем файл, размер ротации и сжатие
logger.add("../setting/log/log.log", rotation="1 MB", compression="zip")


async def main():
    """
    Главная асинхронная функция для запуска бота.
    Здесь инициализируются обработчики команд и запускается polling.
    """
    try:
        logger.info("Бот запущен")
        # router.message.register(handle_text_messages)
        router.chat_member.register(handle_new_member)
        router.chat_member.register(handle_member_left)
        router.message.register(delete_system_message_new_member)
        router.message.register(delete_system_message_member_left)
        router.message.register(check_subscription)
        router.message.register(on_chat_member_update)

        await dp.start_polling(bot)

    except Exception as error:
        # Логирование исключений, если что-то пошло не так
        logger.exception(error)


# Точка входа в программу
if __name__ == "__main__":
    # Запуск асинхронной главной функции
    asyncio.run(main())
