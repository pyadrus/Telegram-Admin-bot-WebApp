# -*- coding: utf-8 -*-
import re

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery
from aiogram.types import Message
from groq import Groq
from loguru import logger
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest

from scr.YandexWordstatPy.yandex_wordstat_py import yandex_wordstat_py
from scr.bot.system.dispatcher import api_id, api_hash, GROQ_KEY, OAuth, SESSION_NAME, USER, PASSWORD, IP, PORT
from scr.bot.system.dispatcher import router
from scr.proxy.proxy import setup_proxy


async def get_chat_completion(work: str) -> str:
    """Возвращает ключевые слова из текста поста через ИИ"""
    setup_proxy(USER, PASSWORD, IP, PORT)
    try:
        client = Groq(api_key=GROQ_KEY)
        chat_completion = client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=[
                {"role": "system",
                 "content": "Проанализируй текст и найди ключевые словосочетания. Обрати внимание, что мне не нужно писать "
                            "много текста, мне нужен просто список словосочетаний без 1,2,3 и без лишнего текста. "
                            "Нужно не более 5 ключевых словосочетаний"},
                {"role": "user", "content": work},  # <-- используем текст поста
            ],
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        logger.exception(e)
        return "⚠️ Ошибка при обращении к ИИ"


class AnalysisState(StatesGroup):
    link_post = State()


def ai_text_to_list(text: str) -> list[str]:
    """
    Преобразует многострочный текст в список строк.
    Убирает пустые строки и пробелы по краям.
    """
    return [line.strip() for line in text.splitlines() if line.strip()]


def pretty_regions(data: dict) -> str:
    result = [f"📊 Региональная статистика для запроса: {data['requestPhrase']}"]
    for region in data.get("regions", []):
        result.append(f"   • {region['regionName']} — {region['count']:,}")
    return "\n".join(result)


@router.callback_query(lambda c: c.data == "analysis")
async def analysis_callback(callback: CallbackQuery, state: FSMContext):
    """Отвечает на нажатие кнопки 'Анализ'"""

    msg = await callback.message.answer(
        "Пришлите ссылку на пост в Telegram для анализа поисковых запроссов по ключевым словам:")
    await state.update_data(prompt_msg_id=msg.message_id)  # сохраним id сообщения для удаления

    # Переводим пользователя в состояние ожидания ссылки
    await state.set_state(AnalysisState.link_post)
    await callback.answer()


# Хендлер получения ссылки от пользователя
@router.message(AnalysisState.link_post)
async def get_link_post_user(message: Message, state: FSMContext):
    """Получает ссылку от пользователя"""

    data = await state.get_data()
    prompt_msg_id = data.get("prompt_msg_id")

    # Удаляем сообщение бота "Пришлите ссылку..."
    if prompt_msg_id:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=prompt_msg_id)
        except Exception as e:
            logger.warning(f"Не удалось удалить сообщение: {e}")

    # Удаляем сообщение пользователя со ссылкой
    try:
        await message.delete()
    except Exception as e:
        logger.warning(f"Не удалось удалить сообщение пользователя: {e}")

    link = message.text.strip()
    logger.info(f"Получена ссылка: {link}")
    # Сохраним ссылку в FSM (на всякий случай)
    await state.update_data(link_post=link)
    await state.clear()

    await message.answer(
        text=f"✅ Ссылка получена:\n{link}",
        disable_web_page_preview=True  # отключаем превью в Telegram
    )

    # --- Разбираем ссылку ---
    match_public = re.match(r"https://t\.me/([^/]+)/(\d+)", link)
    match_private = re.match(r"https://t\.me/c/(\d+)/(\d+)", link)
    logger.info(f"match_public: {match_public}, match_private: {match_private}")
    channel, message_id = None, None
    if match_public:
        channel = match_public.group(1)  # username канала
        message_id = int(match_public.group(2))  # id поста
    elif match_private:
        channel_id = int(match_private.group(1))
        message_id = int(match_private.group(2))
        channel = int(f"-100{channel_id}")  # приватные каналы в формате -100XXXXXXXXXX
    else:
        await message.answer("⚠️ Неверная ссылка. Пришлите ссылку на пост вида https://t.me/username/123")
        return

    # --- Работаем с Telethon ---
    async with TelegramClient(f"scr/setting/{SESSION_NAME}", api_id, api_hash) as client:
        await client.connect()
        try:
            # Если канал публичный — подписываемся
            if isinstance(channel, str):
                try:
                    await client(JoinChannelRequest(channel))
                except Exception as e:
                    logger.warning(f"Не удалось подписаться: {e}")
            # Получаем сообщение
            msg = await client.get_messages(channel, ids=message_id)
            logger.info(f"Получено сообщение: {msg}")
            post_text = msg.text  # вот здесь текст поста
            logger.info(f"Получен текст поста: {post_text}")
            if not msg:
                await message.answer("⚠️ Пост не найден.")
                return
            post_text = msg.text or ""  # .message устарело, лучше использовать .text
            if not post_text.strip():
                await message.answer("⚠️ Пост без текста (возможно только медиа).")
                return
            # Отправляем в ИИ для анализа
            ai_answer = await get_chat_completion(work=post_text)
            await message.answer(f"📌 Ключевые слова:\n{ai_answer}")
            keywords = ai_text_to_list(ai_answer)
            logger.debug(keywords)
        except Exception as e:
            logger.error(f"Ошибка анализа поста: {e}")
            await message.answer("⚠️ Ошибка при обработке поста.")

    # --- Работаем с Wordstat ---

    for keyword in keywords:
        yandex_wordstat_py(keyword, OAuth)


def register_analysis_handler() -> None:
    router.callback_query.register(analysis_callback)
    router.message.register(get_link_post_user, AnalysisState.link_post)
