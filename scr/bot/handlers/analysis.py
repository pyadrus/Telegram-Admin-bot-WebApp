# -*- coding: utf-8 -*-
import os
import re

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery
from aiogram.types import Message
from dotenv import load_dotenv
from groq import Groq
from loguru import logger
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from loguru import logger
from scr.bot.system.dispatcher import api_id, api_hash
from scr.bot.system.dispatcher import router

SESSION_NAME = "session_name_1"

load_dotenv(dotenv_path='.env')

GROQ_KEY = os.getenv('GROQ_KEY')  # GROQ_KEY
USER = os.getenv('USER')  # логин для прокси
PASSWORD = os.getenv('PASSWORD')  # пароль для прокси
PORT = os.getenv('PORT')  # порт для прокси
IP = os.getenv('IP')  # IP для прокси


def setup_proxy():
    # Указываем прокси для HTTP и HTTPS
    os.environ['http_proxy'] = f"http://{USER}:{PASSWORD}@{IP}:{PORT}"
    os.environ['https_proxy'] = f"http://{USER}:{PASSWORD}@{IP}:{PORT}"


async def get_chat_completion(message: Message, work):
    """Возвращает ответ пользователя"""
    setup_proxy()
    try:
        client = Groq(api_key=GROQ_KEY)

        chat_completion = client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=[
                {"role": "system", "content": "Проанализируй текст и найди ключевые слова."},
                {"role": "user", "content": message.text},
            ],
        )

        return chat_completion.choices[0].message.content
    except Exception as e:
        logger.exception(e)


class AnalysisState(StatesGroup):
    link_post = State()


@router.callback_query(lambda c: c.data == "analysis")
async def analysis_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Пришлите ссылку на пост в Telegram для анализа поисковых запроссов по ключевым словам:")
    # Переводим пользователя в состояние ожидания ссылки
    await state.set_state(AnalysisState.link_post)
    await callback.answer()


# Хендлер получения ссылки от пользователя
@router.message(AnalysisState.link_post)
async def get_link_post_user(message: Message, state: FSMContext):
    link = message.text.strip()
    logger.info(f"Получена ссылка: {link}")
    # Сохраним ссылку в FSM (на всякий случай)
    await state.update_data(link_post=link)
    await state.clear()

    await message.answer(f"✅ Ссылка получена:\n{link}")

    # --- Разбираем ссылку ---
    match_public = re.match(r"https://t\.me/([^/]+)/(\d+)", link)
    match_private = re.match(r"https://t\.me/c/(\d+)/(\d+)", link)
    logger.info(f"match_public: {match_public}, match_private: {match_private}")
    channel, message_id = None, None

    if match_public:
        channel = match_public.group(1)         # username канала
        message_id = int(match_public.group(2)) # id поста
    elif match_private:
        channel_id = int(match_private.group(1))
        message_id = int(match_private.group(2))
        channel = int(f"-100{channel_id}")      # приватные каналы в формате -100XXXXXXXXXX
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



            if not msg:
                await message.answer("⚠️ Пост не найден.")
                return

            post_text = msg.text or ""  # .message устарело, лучше использовать .text

            if not post_text.strip():
                await message.answer("⚠️ Пост без текста (возможно только медиа).")
                return

            # Отправляем в ИИ для анализа
            ai_answer = await get_chat_completion(message=message, work=post_text)

            await message.answer(f"📌 Ключевые слова:\n{ai_answer}")

        except Exception as e:
            logger.error(f"Ошибка анализа поста: {e}")
            await message.answer("⚠️ Ошибка при обработке поста.")


def register_analysis_handler() -> None:
    router.callback_query.register(analysis_callback)
    router.message.register(get_link_post_user, AnalysisState.link_post)
