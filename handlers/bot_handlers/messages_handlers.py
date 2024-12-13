import asyncio

from aiogram import F
from aiogram.types import ContentType
from aiogram.types import Message
from loguru import logger

from messages.user_messages import username_admin
from system.dispatcher import dp, bot, time_del
from system.sqlite import fetch_user_data


@dp.message(F.content_type == ContentType.STICKER)
async def handle_sticker_message(message: Message) -> None:
    """
    Обработчик сообщений со стикерами. Удаляет стикеры, отправленные пользователями,
    если их ID не зарегистрированы в базе данных. Отправляет предупреждение, если
    стикеры запрещены в чате.

    Аргументы:
    :param message: (Message): Сообщение Telegram, содержащее стикер.
    :return: None
    """

    # Получение данных из базы данных
    data_dict = fetch_user_data()
    chat_id = message.chat.id
    user_id = message.from_user.id
    # Логирование ID пользователя и чата для отладки
    logger.info(f"Получен ID пользователя: {user_id}")
    logger.info(f"Chat ID: {chat_id}, User ID: {user_id}")

    if (message.chat.id, message.from_user.id) in data_dict:
        logger.info(f"{str(message.from_user.full_name)} отправил стикер в группу")
    else:
        # Удаление стикера
        await bot.delete_message(chat_id, message.message_id)  # Удаляем сообщение
        # Отправляем сообщение в группу
        warning = await message.answer(f"<code>✅ {str(message.from_user.full_name)}</code>\n"
                                       f"<code>В чате запрещено отправлять стикеры, для получения разрешения напишите "
                                       f"админу</code> ➡️ {username_admin}", parse_mode="HTML")
        await asyncio.sleep(int(time_del))  # Спим 20 секунд
        await warning.delete()  # Удаляем предупреждение от бота


def register_message_handlers():
    """
    Регистрирует обработчики событий для бота.

    Обработчики включают удаление запрещенных сообщений, таких как стикеры,
    и другие действия, связанные с событиями в чате.
    """
    dp.message.register(handle_sticker_message, F.content_type == ContentType.STICKER)
