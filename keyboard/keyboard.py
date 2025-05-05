from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def create_group_participants_button():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        text='Получить количество участников в группе',
        callback_data='get_number_participants_group'
    )]])
