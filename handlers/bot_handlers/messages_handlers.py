import asyncio
from aiogram import F
from aiogram.types import ContentType, Message
from loguru import logger

from messages.user_messages import username_admin
from system.dispatcher import dp, bot, time_del
from system.sqlite import fetch_user_data, reading_from_the_database_of_forbidden_words, \
    recording_actions_in_the_database


async def process_forwarded_message(message: Message, data_dict: dict) -> None:
    """
    Обрабатывает пересылаемые сообщения, удаляя их, если пользователь не имеет разрешения.

    :param message: Сообщение Telegram.
    :param data_dict: Словарь зарегистрированных пользователей.
    """
    chat_id = message.chat.id
    user_id = message.from_user.id

    if (chat_id, user_id) in data_dict:
        logger.info(f"{message.from_user.full_name} переслал сообщение.")
    else:
        await bot.delete_message(chat_id, message.message_id)
        warning = await message.answer(
            f"<code>✅ {message.from_user.full_name}</code>\n"
            f"<code>В чате запрещены пересылаемые сообщения. Напишите админу:</code> ➡️ {username_admin}",
            parse_mode="HTML",
        )
        await asyncio.sleep(int(time_del))
        await warning.delete()


async def process_mentions(message: Message, data_dict: dict) -> None:
    """
    Обрабатывает сообщения с упоминаниями, удаляя их, если пользователь не имеет разрешения.

    :param message: Сообщение Telegram.
    :param data_dict: Словарь зарегистрированных пользователей.
    """
    chat_id = message.chat.id
    user_id = message.from_user.id

    for entity in message.entities or []:
        if entity.type == "mention":
            if (chat_id, user_id) in data_dict:
                logger.info(f"{message.from_user.full_name} написал сообщение с упоминанием.")
            else:
                await bot.delete_message(chat_id, message.message_id)
                warning = await message.answer(
                    f"<code>✅ {message.from_user.full_name}</code>\n"
                    f"<code>В чате запрещено использование упоминаний. Напишите админу:</code> ➡️ {username_admin}",
                    parse_mode="HTML",
                )
                await asyncio.sleep(int(time_del))
                await warning.delete()


async def process_sticker_message(message: Message, data_dict: dict) -> None:
    """
    Обрабатывает сообщения со стикерами, удаляя их, если пользователь не имеет разрешения.

    :param message: Сообщение Telegram.
    :param data_dict: Словарь зарегистрированных пользователей.
    """
    chat_id = message.chat.id
    user_id = message.from_user.id

    if (chat_id, user_id) in data_dict:
        logger.info(f"{message.from_user.full_name} отправил стикер в группу.")
    else:
        await bot.delete_message(chat_id, message.message_id)
        warning = await message.answer(
            f"<code>✅ {message.from_user.full_name}</code>\n"
            f"<code>В чате запрещено отправлять стикеры. Напишите админу:</code> ➡️ {username_admin}",
            parse_mode="HTML",
        )
        await asyncio.sleep(int(time_del))
        await warning.delete()


@dp.message(F.content_type == ContentType.TEXT)
async def handle_text_messages(message: Message) -> None:
    """
    Основной обработчик текстовых сообщений. Обрабатывает пересылаемые сообщения, упоминания, запрещенные слова и ссылки.

    :param message: Сообщение Telegram.
    """
    logger.info(f"Обработка текстового сообщения от {message.from_user.full_name}.")
    data_dict = fetch_user_data()

    try:
        if message.forward_from or message.forward_from_chat:
            await process_forwarded_message(message, data_dict)
        else:
            await process_mentions(message, data_dict)

        # Проверка на запрещенные слова
        bad_words = reading_from_the_database_of_forbidden_words()
        for word in bad_words:
            if word[0] in message.text.lower():
                recording_actions_in_the_database(word[0], message)
                await message.delete()
                warning = await bot.send_message(
                    message.chat.id,
                    f'В вашем сообщении обнаружено запрещенное слово. Пожалуйста, не используйте его в дальнейшем.'
                )
                await asyncio.sleep(int(time_del))
                await warning.delete()

        # Проверка на ссылки
        for entity in message.entities or []:
            if entity.type in ["url", "text_link"]:
                if (message.chat.id, message.from_user.id) in data_dict:
                    logger.info(f"{message.from_user.full_name} написал сообщение со ссылкой.")
                else:
                    await bot.delete_message(message.chat.id, message.message_id)
                    warning = await message.answer(
                        f"<code>✅ {message.from_user.full_name}</code>\n"
                        f"<code>В чате запрещена публикация сообщений со ссылками. Напишите админу:</code> ➡️ {username_admin}",
                        parse_mode="HTML",
                    )
                    await asyncio.sleep(int(time_del))
                    await warning.delete()

    except Exception as e:
        logger.error(f"Ошибка при обработке текстового сообщения: {e}")


@dp.message(F.content_type == ContentType.STICKER)
async def handle_sticker_messages(message: Message) -> None:
    """
    Обработчик сообщений со стикерами. Удаляет стикеры, если пользователь не имеет разрешения.

    :param message: Сообщение Telegram.
    """
    logger.info(f"Обработка стикера от {message.from_user.full_name}.")
    data_dict = fetch_user_data()

    try:
        await process_sticker_message(message, data_dict)
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения со стикером: {e}")


def register_message_handlers() -> None:
    """
    Регистрирует обработчики событий для бота.
    """
    dp.message.register(handle_text_messages)
    dp.message.register(handle_sticker_messages)
