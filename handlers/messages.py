import asyncio

from aiogram.types import Message
from loguru import logger

from keyboard.keyboard import create_admin_panel_keyboard
from messages.translations_loader import translations
from system.dispatcher import router, bot, time_del
from utils.models import BadWords, PrivilegedUsers


def get_privileged_users():
    """
    Получает список привилегированных пользователей (chat_id, user_id)
    """
    try:
        query = PrivilegedUsers.select(
            PrivilegedUsers.chat_id, PrivilegedUsers.user_id)
        return {(row.chat_id, row.user_id) for row in query}
    except Exception as e:
        print(f"Ошибка при получении привилегированных пользователей: {e}")
        return set()


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
                    f"<code>✅ {message.from_user.full_name}</code>\n"
                    f"<code>В чате запрещены пересылаемые сообщения.</code>",
                    parse_mode="HTML",
                )
                await asyncio.sleep(int(time_del))
                await warning.delete()
            return
        # Вывод запрещенных слов с чисткой дублей
        bad_words = list(set(word.bad_word for word in BadWords.select()))
        print(bad_words)
        # Проверка на запрещенные слова
        for word in bad_words:
            if word[0].lower() in message.text.lower():
                # recording_actions_in_the_database(word[0], message)
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
