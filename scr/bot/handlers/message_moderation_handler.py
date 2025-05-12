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
    logger.debug(f"Получено сообщение от пользователя {message.from_user.id}")
    user_id = message.from_user.id
    logger.debug(f"Пользователь {user_id}")

    if message.text == "/start":
        logger.info(f"Пользователь {user_id} прислал команду /start")
        user_id = message.from_user.id
        keyboard = create_admin_panel_keyboard(user_id)

        await bot.send_message(
            message.chat.id,
            translations["ru"]["menu"]["user"],
            reply_markup=keyboard,
            parse_mode="HTML"
        )

    try:
        # Проверка на пересылку сообщений
        if message.forward_from or message.forward_from_chat:
            privileged_users = get_privileged_users()
            if (chat_id, user_id) not in privileged_users:
                await message.delete()
                warning = await message.answer(
                    text=translations["ru"]["message_moderation"]["moderation_forward_message"],
                    parse_mode="HTML",
                )
                await asyncio.sleep(int(time_del))
                await warning.delete()
            return

        if message.text:
            # Вывод запрещенных слов с чисткой дублей
            bad_words = list(set(word.bad_word for word in BadWords.select()))
            print(bad_words)
            # Проверка на запрещенные слова
            for word in bad_words:
                if word[0].lower() in message.text.lower():
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
                    return  # После удаления сообщения больше ничего не проверяем

        # Проверка на ссылки
        if message.text and message.entities:
            for entity in message.entities:
                if entity.type in ["url", "text_link", "mention"]:
                    privileged_users = get_privileged_users()
                    if (chat_id, user_id) not in privileged_users:
                        await message.delete()
                        warning = await message.answer(
                            text=translations["ru"]["message_moderation"]["moderation_url_message"],
                            parse_mode="HTML",
                        )
                        await asyncio.sleep(int(time_del))
                        await warning.delete()
                        return  # После удаления сообщения больше ничего не проверяем

    except Exception as e:
        logger.exception(f"{e}")


def register_text_messages_handlers() -> None:
    router.message.register(message_moderation_handler)
