# -*- coding: utf-8 -*-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

"""Проверка на ID"""
# def create_admin_panel_keyboard(user_id: int) -> InlineKeyboardMarkup:
#     """Клавиатура для главного меню (с проверкой ID)"""
#     buttons = []
#
#     # Показываем кнопку только если ID совпадает
#     if user_id == 535185511:
#         buttons.append(
#             [
#                 InlineKeyboardButton(
#                     text="Панель администратора",
#                     web_app=WebAppInfo(url="https://mybotadmin.ru.tuna.am"),
#                 )
#             ]
#         )
#
#     return InlineKeyboardMarkup(inline_keyboard=buttons)


"""Без проверки"""
def create_admin_panel_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для главного меню"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Панель администратора",
                    web_app=WebAppInfo(url="https://mybotadmin.ru.tuna.am"),
                )
            ]
        ]
    )
    return keyboard
