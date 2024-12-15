import asyncio

from aiogram import F
from aiogram.types import ContentType, Message
from loguru import logger

from handlers.user_handlers.user_handlers import read_json_file
from system.dispatcher import time_del, router
from system.sqlite import fetch_user_data, reading_from_the_database_of_forbidden_words, \
    recording_actions_in_the_database


@router.message(F.content_type == ContentType.TEXT)
async def handle_text_messages(message: Message) -> None:
    """
    Основной обработчик текстовых сообщений. Обрабатывает пересылаемые сообщения, упоминания, запрещенные слова и ссылки.

    :param message: Сообщение Telegram.
    """

    logger.info(f"Обработка текстового сообщения от {message.from_user.full_name}.")
    chat_id = message.chat.id
    user_id = message.from_user.id

    try:
        if message.text == "/help":
            await message.answer(read_json_file("messages/bot_commands.json"), parse_mode="HTML")
    except Exception as e:
        logger.error(f"Ошибка в обработчике /help: {e}")

    try:
        if message.text == "/start":
            user_id = message.from_user.id
            user_name = message.from_user.username or ""
            user_first_name = message.from_user.first_name or ""
            user_last_name = message.from_user.last_name or ""
            user_date = message.date.strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"User Info: {user_id}, {user_name}, {user_first_name}, {user_last_name}, {user_date}")
            await message.answer(read_json_file("messages/start_messages.json"), parse_mode="HTML")
    except Exception as e:
        logger.error(f"Ошибка в обработчике /start: {e}")

    try:
        # Проверка на пересылку сообщений
        if message.forward_from or message.forward_from_chat:
            data_dict = fetch_user_data()
            if (chat_id, user_id) not in data_dict:
                await message.delete()
                warning = await message.answer(
                    f"<code>✅ {message.from_user.full_name}</code>\n"
                    f"<code>В чате запрещены пересылаемые сообщения.</code>",
                    parse_mode="HTML",
                )
                await asyncio.sleep(int(time_del))
                await warning.delete()
            return

        # Проверка на запрещенные слова
        bad_words = reading_from_the_database_of_forbidden_words()
        for word in bad_words:
            if word[0].lower() in message.text.lower():
                recording_actions_in_the_database(word[0], message)
                await message.delete()
                warning = await message.answer(
                    f"⚠ В вашем сообщении обнаружено запрещенное слово: <code>{word[0]}</code>. "
                    f"Пожалуйста, не используйте его в дальнейшем.",
                    parse_mode="HTML",
                )
                await asyncio.sleep(int(time_del))
                await warning.delete()
                return  # После удаления сообщения больше ничего не проверяем

        # Проверка на ссылки
        for entity in message.entities or []:
            if entity.type in ["url", "text_link", "mention"]:
                data_dict = fetch_user_data()
                if (chat_id, user_id) not in data_dict:
                    await message.delete()
                    warning = await message.answer(
                        f"<code>✅ {message.from_user.full_name}</code>\n"
                        f"<code>В чате запрещена публикация сообщений со ссылками.</code>",
                        parse_mode="HTML",
                    )
                    await asyncio.sleep(int(time_del))
                    await warning.delete()
                    return  # После удаления сообщения больше ничего не проверяем


    except Exception as e:
        logger.error(f"Ошибка при обработке текстового сообщения: {e}")


# Функция-обработчик стикеров
@router.message(F.content_type == ContentType.STICKER)
async def handle_sticker_messages(message: Message) -> None:
    """
    Обработчик сообщений со стикерами. Удаляет стикеры, если пользователь не имеет разрешения.

    :param message: Сообщение Telegram.
    """
    if not message.from_user:
        logger.warning("Сообщение без отправителя (from_user отсутствует).")
        return

    logger.info(f"Обработка стикера от {message.from_user.full_name}.")

    # Получение данных пользователей
    data_dict = fetch_user_data()  # Убедитесь, что эта функция возвращает корректный словарь

    chat_id = message.chat.id
    user_id = message.from_user.id

    # Проверяем, есть ли пользователь в списке разрешенных
    if (chat_id, user_id) in data_dict:
        logger.info(f"{message.from_user.full_name} отправил стикер в группу.")
    else:
        # Удаляем сообщение
        await message.delete()
        warning = await message.answer(
            f"<code>✅ {message.from_user.full_name}</code>\n"
            f"<code>В чате запрещено отправлять стикеры.</code>",
            parse_mode="HTML",
        )
        await asyncio.sleep(int(time_del))
        await warning.delete()


def register_message_handlers() -> None:
    """
    Регистрирует обработчики событий для бота.
    """
    router.message.register(handle_text_messages)
    router.message.register(handle_sticker_messages)
