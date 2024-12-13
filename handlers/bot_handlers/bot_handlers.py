import datetime

from aiogram import F
from aiogram.types import ContentType
from aiogram.types import Message

# Импорты из системы
from system.dispatcher import dp, bot  # Диспетчер и бот
from system.sqlite import writing_to_the_database_about_a_new_user  # Функция записи данных в базу


@dp.message(F.content_type == ContentType.NEW_CHAT_MEMBERS)
async def deleting_message_about_adding_new_group_member(message: Message):
    """
    Обработчик события добавления нового участника в группу.
    Удаляет сообщение о новом участнике и записывает данные в базу.
    """

    date_now = datetime.datetime.now()  # Текущая дата и время

    # Получаем данные о чате и новом участнике
    chat_id = message.chat.id  # ID чата
    chat_title = message.chat.title  # Название чата
    user_id = message.new_chat_members[0].id  # ID нового участника
    username = message.new_chat_members[0].username  # Username нового участника
    first_name = message.new_chat_members[0].first_name  # Имя нового участника
    last_name = message.new_chat_members[0].last_name  # Фамилия нового участника

    # Удаляем сообщение о добавлении нового участника
    await bot.delete_message(chat_id, message.message_id)

    # Имя таблицы для записи данных
    name_table = "group_members_add"

    # Записываем данные о новом участнике в базу данных
    writing_to_the_database_about_a_new_user(
        name_table, chat_id, chat_title, user_id, username, first_name, last_name, date_now
    )


@dp.message(F.content_type == ContentType.LEFT_CHAT_MEMBER)
async def deleting_a_message_about_a_member_has_left_the_group(message: Message):
    """
    Обработчик события выхода участника из группы.
    Удаляет сообщение о выходе и записывает данные в базу.
    """

    date_left = datetime.datetime.now()  # Текущая дата и время (момент выхода)

    # Получаем данные о чате и вышедшем участнике
    chat_id = message.chat.id  # ID чата
    chat_title = message.chat.title  # Название чата
    user_id = message.left_chat_member.id  # ID вышедшего участника
    username = message.left_chat_member.username  # Username вышедшего участника
    first_name = message.left_chat_member.first_name  # Имя вышедшего участника
    last_name = message.left_chat_member.last_name  # Фамилия вышедшего участника

    # Удаляем сообщение о выходе участника
    await bot.delete_message(message.chat.id, message.message_id)

    # Имя таблицы для записи данных
    name_table = "group_members_left"

    # Записываем данные о вышедшем участнике в базу данных
    writing_to_the_database_about_a_new_user(
        name_table, chat_id, chat_title, user_id, username, first_name, last_name, date_left
    )


def register_bot_handlers():
    """
    Регистрация обработчиков событий для бота.
    Добавляет обработчики событий для добавления/выхода участников группы.
    """
    dp.message.register(deleting_message_about_adding_new_group_member)
    dp.message.register(deleting_a_message_about_a_member_has_left_the_group)
