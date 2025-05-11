from aiogram.fsm.state import StatesGroup, State


class AddUserStates(StatesGroup):
    """
    Класс состояний для добавления пользователя.

    :cvar WAITING_FOR_USER_ID: Состояние ожидания ID пользователя.
    """
    WAITING_FOR_USER_ID = State()
