# -*- coding: utf-8 -*-
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message

from scr.bot.system.dispatcher import router


class AnalysisState(StatesGroup):
    link_post = State()

@router.callback_query(lambda c: c.data == "analysis")
async def analysis_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Пришлите ссылку на пост в Telegram для анализа поисковых запроссов по ключевым словам:")
    # Переводим пользователя в состояние ожидания ссылки
    await state.set_state(AnalysisState.link_post)
    await callback.answer()

# Хендлер получения ссылки от пользователя
@router.message(AnalysisState.link_post)
async def get_link_post_user(message: Message, state: FSMContext):
    link = message.text  # тут будет ссылка, которую прислал пользователь

    # можешь сразу сохранить в FSM
    await state.update_data(link_post=link)

    await message.answer(f"✅ Ссылка получена:\n{link}")

    # если после этого состояние больше не нужно — сбрасываем
    await state.clear()


def register_analysis_handler() -> None:
    router.callback_query.register(analysis_callback)
    router.message.register(get_link_post_user, AnalysisState.link_post)
