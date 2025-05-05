from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

def create_group_participants_button():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        text='Получить количество участников в группе',
        callback_data='get_number_participants_group'
    )]])


def create_admin_panel_keyboard():
    """Клавиатура для главного меню"""
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Панель администратора',
                                                                       web_app=WebAppInfo(url="https://adminbot.ru.tuna.am"))]])