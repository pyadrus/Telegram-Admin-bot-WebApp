import datetime

from aiogram import F
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from aiogram.types import ChatMemberUpdated
from aiogram.types import Message
from loguru import logger

# Импорты из системы
from system.dispatcher import dp  # Экземпляр диспетчера (бота и роутера)
from system.sqlite import writing_to_the_database_about_a_new_user  # Функция для записи данных в базу данных


@dp.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def handle_new_member(event: ChatMemberUpdated):
    """
    Обработчик события добавления нового участника в группу.
    Записывает информацию о новом участнике в базу данных.

    IS_NOT_MEMBER >> IS_MEMBER - Участник только что присоединился к группе.
    (https://docs.aiogram.dev/en/latest/dispatcher/filters/chat_member_updated.html#usage)
    """
    try:
        current_datetime = datetime.datetime.now()  # Текущее время

        # Извлечение данных о группе и участнике
        group_id = event.chat.id
        group_title = event.chat.title
        user_id = event.from_user.id
        user_username = event.from_user.username
        user_first_name = event.from_user.first_name
        user_last_name = event.from_user.last_name

        # Логируем событие добавления участника
        logger.info(
            f"Новый участник: {user_first_name} {user_last_name} (username: {user_username}, id: {user_id}) присоединился к группе '{group_title}' (id: {group_id})."
        )

        # Имя таблицы для записи информации о новых участниках
        database_table_name = "group_members_add"

        # Записываем данные о новом участнике в базу данных
        writing_to_the_database_about_a_new_user(
            database_table_name, group_id, group_title, user_id, user_username,
            user_first_name, user_last_name, current_datetime
        )

    except Exception as error:
        logger.exception(f"Ошибка обработки добавления нового участника: {error}")


@dp.chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
async def handle_member_left(event: ChatMemberUpdated):
    """
    Обработчик события выхода участника из группы.
    Записывает информацию о вышедшем участнике в базу данных.

    IS_MEMBER >> IS_NOT_MEMBER - Участник только что покинул группу.
    (https://docs.aiogram.dev/en/latest/dispatcher/filters/chat_member_updated.html#usage)
    """
    try:
        current_datetime = datetime.datetime.now()  # Текущее время

        # Извлечение данных о группе и участнике
        group_id = event.chat.id
        group_title = event.chat.title
        user_id = event.from_user.id
        user_username = event.from_user.username
        user_first_name = event.from_user.first_name
        user_last_name = event.from_user.last_name

        # Логируем событие выхода участника
        logger.info(
            f"Участник: {user_first_name} {user_last_name} (username: {user_username}, id: {user_id}) покинул группу '{group_title}' (id: {group_id}) в {current_datetime}."
        )

        # Имя таблицы для записи информации о вышедших участниках
        database_table_name = "group_members_left"

        # Записываем данные о вышедшем участнике в базу данных
        writing_to_the_database_about_a_new_user(
            database_table_name, group_id, group_title, user_id, user_username,
            user_first_name, user_last_name, current_datetime
        )

    except Exception as error:
        logger.exception(f"Ошибка обработки выхода участника: {error}")


@dp.message(F.new_chat_members)
async def delete_system_message_new_member(message: Message):
    """
    Обработчик удаления системного сообщения о вступлении нового участника в группу.

    Тип сообщения: new_chat_members (https://docs.aiogram.dev/en/v3.1.1/api/enums/content_type.html)
    """
    await message.delete()  # Удаляем системное сообщение


@dp.message(F.left_chat_member)
async def delete_system_message_member_left(message: Message):
    """
    Обработчик удаления системного сообщения о выходе участника из группы.

    Тип сообщения: left_chat_member (https://docs.aiogram.dev/en/v3.1.1/api/enums/content_type.html)
    """
    await message.delete()  # Удаляем системное сообщение


def register_bot_handlers():
    """
    Регистрация обработчиков событий для бота.
    Добавляет обработчики событий на добавление и выход участников, а также на удаление системных сообщений.
    """
    dp.chat_member.register(handle_new_member)
    dp.chat_member.register(handle_member_left)
    dp.message.register(delete_system_message_new_member)
    dp.message.register(delete_system_message_member_left)
