from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from states.states import GetCountMembers
from system.dispatcher import bot, router


@router.callback_query(F.data == "get_number_participants_group")
async def get_count_members(callback_query: CallbackQuery, state: FSMContext):
    """Начало процесса получения количества участников"""
    await callback_query.answer()
    await bot.send_message(
        callback_query.from_user.id,
        'Введите идентификатор группы для отслеживания (пример: -1001234567890):'
    )
    await state.set_state(GetCountMembers.get_count_members_grup)  # Исправлено!


@router.message(GetCountMembers.get_count_members_grup)
async def get_count_members_state(message: Message, state: FSMContext):
    """Получить количество участников в указанной группе"""
    try:
        chat_id = int(message.text)
        chat = await bot.get_chat(chat_id)
        await message.answer(f'Количество участников в группе: {chat.member_count}')
    except ValueError:
        await message.answer('Ошибка! Введите корректный идентификатор группы (пример: -1001234567890).')
    except Exception as e:
        await message.answer(f'Ошибка при получении данных: {e}')
    finally:
        await state.clear()


def regis_count_members():
    router.callback_query.register(get_count_members, F.data == "get_number_participants_group")
    router.message.register(get_count_members_state, GetCountMembers.get_count_members_grup)
