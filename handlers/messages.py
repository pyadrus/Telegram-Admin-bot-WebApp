import asyncio

from aiogram.types import Message
from loguru import logger

from system.dispatcher import router, time_del
from system.sqlite import (fetch_user_data,
                           recording_actions_in_the_database)
from utils.models import reading_from_the_database_of_forbidden_words


@router.message()
async def handle_text_messages(message: Message) -> None:
    """
    Основной обработчик текстовых сообщений. Обрабатывает пересылаемые сообщения, упоминания, запрещенные слова и ссылки.

    :param message: Сообщение Telegram.
    """
    logger.debug("Хендлер сработал")
    chat_id = message.chat.id
    logger.debug(f"Получено сообщение от пользователя {message.from_user.id}")
    user_id = message.from_user.id
    logger.debug(f"Пользователь {user_id}")

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
        for word in reading_from_the_database_of_forbidden_words():
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
                if (chat_id, user_id) not in fetch_user_data():
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
