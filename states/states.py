from aiogram.fsm.state import StatesGroup, State


class AddAndDelBadWords(StatesGroup):
    """Создаем состояние для добавления плохих слов"""
    waiting_for_bad_word = State()
    waiting_for_check_word = State()
    del_for_bad_word = State()
