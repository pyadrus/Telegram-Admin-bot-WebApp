import asyncio

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from loguru import logger

from scr.bot.keyboard.keyboard import create_admin_panel_keyboard
from scr.bot.messages.translations_loader import translations
from scr.bot.system.dispatcher import router, bot, time_del
from scr.utils.models import BadWords, get_privileged_users


@router.message()
async def message_moderation_handler(message: Message) -> None:
    """
    Основной обработчик текстовых сообщений. Обрабатывает пересылаемые сообщения, упоминания, запрещенные слова и ссылки.

    :param message: Сообщение Telegram.
    """
    logger.debug("Хендлер сработал")
    chat_id = message.chat.id
    user_id = message.from_user.id
    logger.debug(f"Получено сообщение от пользователя {user_id}")
    logger.debug(f"chat_id: {chat_id}, user_id: {user_id}")

    # Нормализуем chat_id и получаем список привилегированных пользователей
    normalized_chat_id = int(str(chat_id).replace("-100", ""))
    privileged_users = get_privileged_users()
    logger.debug(f"privileged_users: {privileged_users}")

    if message.text == "/start":
        logger.info(f"Пользователь {user_id} прислал команду /start")
        keyboard = create_admin_panel_keyboard(user_id)
        await bot.send_message(
            chat_id,
            translations["ru"]["menu"]["user"],
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        return

    try:
        # Пропускаем проверки для привилегированных пользователей
        if (normalized_chat_id, user_id) in privileged_users:
            return

        # Проверка на пересылку сообщений
        if message.forward_from or message.forward_from_chat:
            await message.delete()
            warning = await message.answer(
                text=translations["ru"]["message_moderation"]["moderation_forward_message"],
                parse_mode="HTML",
            )
            await asyncio.sleep(int(time_del))
            await warning.delete()
            return

        if message.text:
            # Получаем запрещённые слова
            bad_words = list(set(word.bad_word for word in BadWords.select()))
            logger.debug(f"Запрещенные слова: {bad_words}")

            # Проверка на запрещённые слова
            for word in bad_words:
                if word.lower() in message.text.lower():
                    try:
                        await message.delete()
                    except TelegramBadRequest:
                        logger.error("Ошибка при удалении сообщения, так как оно уже удалено ранее")
                    warning = await message.answer(
                        text=translations["ru"]["message_moderation"]["moderation_bad_words"],
                        parse_mode="HTML",
                    )
                    await asyncio.sleep(int(time_del))
                    await warning.delete()
                    return

        # Проверка на ссылки
        if message.text and message.entities:
            for entity in message.entities:
                if entity.type in ["url", "text_link", "mention"]:
                    await message.delete()
                    warning = await message.answer(
                        text=translations["ru"]["message_moderation"]["moderation_url_message"],
                        parse_mode="HTML",
                    )
                    await asyncio.sleep(int(time_del))
                    await warning.delete()
                    return

    except Exception as e:
        logger.exception(f"{e}")


def register_text_messages_handlers() -> None:
    router.message.register(message_moderation_handler)
