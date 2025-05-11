from aiogram.fsm.state import StatesGroup, State


class AddUserStates(StatesGroup):
    WAITING_FOR_USER_ID = State()
