import asyncio
import datetime

from aiogram import F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ContentType
from aiogram.types import Message

from messages.user_messages import username_admin, info
from system.dispatcher import dp, bot, time_del
from system.dispatcher import router
from system.sqlite import reading_data_from_the_database
from system.sqlite import reading_from_the_database_of_forbidden_words
from system.sqlite import record_the_id_of_allowed_users
from system.sqlite import recording_actions_in_the_database
from system.sqlite import writing_bad_words_to_the_database
from system.sqlite import writing_to_the_database_about_a_new_user

date_now = datetime.datetime.now()


class AddUserStates(StatesGroup):
    WAITING_FOR_USER_ID = State()  # ожидание ввода ID пользователя;
    USER_ADDED = State()  # состояние, когда пользователь успешно добавлен в базу данных.


class AddAndDelBadWords(StatesGroup):
    """Создаем состояние для добавления плохих слов"""
    waiting_for_bad_word = State()
    waiting_for_check_word = State()
    del_for_bad_word = State()

@router.message(Command("id"))
async def send_id(message: Message, state: FSMContext):
    """Обработчик команды /id"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    print(f"Пользователь {user_id} вызвал команду '/id' в чате {chat_id}")
    # Проверяем, является ли пользователь админом в текущем чате
    chat_member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    if chat_member.status not in ["administrator", "creator"]:
        # Если пользователь не является админом, отправляем ему сообщение с предупреждением
        await bot.send_message(chat_id, "Команда доступна только для администраторов.")
        await message.delete()  # Удаляем сообщение с командой /id
        return
    try:
        # получаем ID пользователя, который написал сообщение
        user_id = message.reply_to_message.from_user.id
        # получаем информацию о пользователе по его ID
        user = await bot.get_chat(user_id)
        # получаем ID, имя и фамилию пользователя
        user_id = user.id
        first_name = user.first_name
        last_name = user.last_name
        # отправляем ID, имя и фамилию пользователя в личку
        await bot.send_message(chat_id=message.from_user.id,
                               text=f'Пользователь: {first_name} {last_name}\nID: {user_id}')
        # удаляем сообщение с командой /id
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except AttributeError:
        # если произошла ошибка AttributeError, то сообщаем об этом пользователю
        await bot.send_message(chat_id=message.chat.id, text='Ответьте на сообщение пользователя, чтобы узнать его ID')
    # except MessageCantBeDeleted:
    #     # если произошла ошибка MessageCantBeDeleted, то сообщаем об этом пользователю
    #     await bot.send_message(chat_id=message.chat.id,
    #                            text='Бот не является админом, нет возможности удалить сообщение')

@router.message(Command("user_add"))
async def cmd_user_add(message: Message, state: FSMContext):
    """Обработчик команды /user_add. Команда /user_add используется для добавления новых пользователей в базу данных
    с определенными правами в группе"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    print(f"Пользователь {user_id} вызвал команду '/user_add' в чате {chat_id}")
    # Проверяем, является ли пользователь админом в текущем чате
    chat_member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    if chat_member.status not in ["administrator", "creator"]:
        # Если пользователь не является админом, отправляем ему сообщение с предупреждением
        await bot.send_message(chat_id, "<code>✅ Команда доступна только для администраторов</code>", parse_mode="HTML")
        await message.delete()  # Удаляем сообщение с командой /user_add
        return
    # Если пользователь является админом, отправляем запрос на ввод ID пользователя
    await message.answer('Введите ID пользователя, для назначения особых прав в группе')
    await state.set_state(AddUserStates.WAITING_FOR_USER_ID)# Переводим бота в состояние WAITING_FOR_USER_ID
    await message.delete()  # Удаляем сообщение с командой /user_add

@router.message(AddUserStates.WAITING_FOR_USER_ID)
async def process_user_id(message: Message, state: FSMContext):
    """Обработчик ввода ID пользователя"""
    try:
        admin_id = message.from_user.id  # Получаем ID админа, который отправил сообщение с ID боту
        user_id = int(message.text)  # Получаем введенный админом ID
        chat_id = message.chat.id  # Получаем ID чата
        chat_title = message.chat.title  # Получаем название чата
        chat_member = await bot.get_chat_member(chat_id, user_id)
        # Получаем username пользователя, который вступил в группу
        username = chat_member.user.username if chat_member.user.username else ""
        # Получаем имя пользователя который вступил в группу
        first_name = chat_member.user.first_name if chat_member.user.first_name else ""
        # Получаем фамилию пользователя который вступил в группу
        last_name = chat_member.user.last_name if chat_member.user.last_name else ""
        record_the_id_of_allowed_users(chat_id, user_id, username, first_name,
                                       last_name, date_now, admin_id, chat_title)  # Записываем данные
        # Отправляем сообщение об успешной записи в чат
        await message.answer(f"<code>✅ Участнику {first_name} {last_name} "
                             f"даны особые права в группе</code> ➡️ {username_admin}", parse_mode="HTML")
        await message.delete()  # Удаляем сообщение с введенным ID пользователя
        await state.clear()  # Сбрасываем состояние FSM
    except ValueError:
        # Если введенный пользователем текст не может быть преобразован в число отправляем сообщение об ошибке
        await message.answer('Введите целое число')
        await message.delete()  # Удаляем сообщение с неправильным вводом

@router.message(Command("add_bad"))
async def cmd_add_bad(message: Message, state: FSMContext):
    """Обработчик команды /add_bad"""
    # Проверяем, вызвал ли команду админ чата
    chat_member = await bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
    if not chat_member.is_chat_admin():
        await message.reply('Эту команду может использовать только администратор чата.')
        return
    await message.answer('✒️ Введите слово, которое нужно добавить ➕ в список 📝 плохих слов 🤬: ',
                         parse_mode="HTML")
    await AddAndDelBadWords.waiting_for_bad_word.set()  # Переходим в состояние ожидания плохого слова

@router.message(AddAndDelBadWords.waiting_for_bad_word)
async def process_bad_word(message: Message, state: FSMContext):
    """Обработчик текстовых сообщений в состоянии ожидания плохого слова"""
    bad_word = message.text.strip().lower()  # Получаем слово от пользователя
    user_id = message.from_user.id  # Получаем ID пользователя
    username = message.from_user.username  # Получаем username пользователя
    user_full_name = message.from_user.full_name  # Получаем Ф.И. пользователя
    chat_id = message.chat.id  # Получаем ID чата / канала
    chat_title = message.chat.title  # Получаем название чата / канала
    writing_bad_words_to_the_database(bad_word, user_id, username, user_full_name, chat_id,
                                      chat_title)  # Запись запрещенных слов в базу данных
    # Выводим сообщение об успешном добавлении слова
    await message.reply('✅ Слово успешно добавлено ➕ в список плохих слов 🤬.', parse_mode="HTML")
    await state.clear()  # Сбрасываем состояние

@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    await message.answer(info, parse_mode="HTML")

@dp.message(F.content_type == ContentType.TEXT)
async def process_message(message: Message):
    """Обрабатываем обычные текстовые сообщения"""

    # Check for forbidden words
    bad_words = reading_from_the_database_of_forbidden_words()
    for word in bad_words:
        if word[0] in message.text.lower():
            recording_actions_in_the_database(word[0], message)
            await message.delete()  # Удаляем сообщение от пользователя с запрещенным словом
            warning = await bot.send_message(message.chat.id, f'В вашем сообщении обнаружено запрещенное слово. '
                                                              f'Пожалуйста, не используйте его в дальнейшем.')
            await asyncio.sleep(int(time_del))  # Спим 20 секунд
            await warning.delete()  # Удаляем предупреждение от бота

    # Check for forbidden links
    for entity in message.entities:
        if entity.type in ["url", "text_link"]:
            # If the user is allowed, don't take any action
            data_dict = reading_data_from_the_database()
            if (message.chat.id, message.from_user.id) in data_dict:
                print(f"{str(message.from_user.full_name)} написал сообщение со ссылкой")
            else:
                await bot.delete_message(message.chat.id, message.message_id)  # Удаляем сообщение
                await message.answer(f"<code>✅ {str(message.from_user.full_name)}</code>\n"
                                     f"<code>В чате запрещена публикация сообщений со ссылками, для получения "
                                     f"разрешения напишите админу</code> ➡️ {username_admin}", parse_mode="HTML")

@dp.message(F.content_type == ContentType.ANY)
async def handle_all_messages(message: Message, state: FSMContext) -> None:
    """Удаляем пересылаемое сообщение"""
    print(message.content_type)  # Выводим тип сообщения в консоль
    """Пересылаемое сообщение"""
    if message.forward_from:
        # Если записанный id пользователя в боте записан, то сообщения пропускаются
        data_dict = reading_data_from_the_database()
        chat_id = message.chat.id
        user_id = message.from_user.id
        print(f"message.from_user.id: {user_id}")
        print(f"chat_id: {chat_id}, user_id: {user_id}")
        if (message.chat.id, message.from_user.id) in data_dict:
            print(f"{str(message.from_user.full_name)} переслал сообщение")
        else:
            await bot.delete_message(message.chat.id, message.message_id)  # Удаляем сообщение
            # Отправляем сообщение в группу
            await message.answer(f"<code>✅ {str(message.from_user.full_name)}</code>\n"
                                 f"<code>В чате запрещены пересылаемые сообщения, для получения разрешения напишите "
                                 f"админу</code> ➡️ {username_admin}", parse_mode="HTML")

    if message.forward_from_chat:
        # Если записанный id пользователя в боте записан, то сообщения пропускаются
        data_dict = reading_data_from_the_database()
        chat_id = message.chat.id
        user_id = message.from_user.id
        print(f"message.from_user.id: {user_id}")
        print(f"chat_id: {chat_id}, user_id: {user_id}")
        if (message.chat.id, message.from_user.id) in data_dict:
            print(f"{str(message.from_user.full_name)} переслал сообщение")
        else:
            await bot.delete_message(message.chat.id, message.message_id)  # Удаляем сообщение
            # Отправляем сообщение в группу
            await message.answer(f"<code>✅ {str(message.from_user.full_name)}</code>\n"
                                 f"<code>В чате запрещены пересылаемые сообщения, для получения разрешения напишите "
                                 f"админу</code> ➡️ {username_admin}", parse_mode="HTML")
    """Сообщения с ссылками"""
    for cap in message.caption_entities:
        # url - обычная ссылка, text_link - ссылка, скрытая под текстом
        if cap.type in ["mention"]:
            # Если записанный id пользователя в боте записан, то сообщения пропускаются
            data_dict = reading_data_from_the_database()
            chat_id = message.chat.id
            user_id = message.from_user.id
            print(f"message.from_user.id: {user_id}")
            print(f"chat_id: {chat_id}, user_id: {user_id}")
            if (message.chat.id, message.from_user.id) in data_dict:
                print(f"{str(message.from_user.full_name)} написал сообщение со ссылкой")
            else:
                await bot.delete_message(message.chat.id, message.message_id)  # Удаляем сообщение
                # Отправляем сообщение в группу
                await message.answer(f"<code>✅ {str(message.from_user.full_name)}</code>\n"
                                     f"<code>В чате запрещена публикация сообщений со ссылками, для получения "
                                     f"разрешения напишите админу</code> ➡️ {username_admin}", parse_mode="HTML")

@dp.message(F.content_type == ContentType.NEW_CHAT_MEMBERS)
async def deleting_message_about_adding_new_group_member(message: Message, state: FSMContext):
    """Удаляем сообщение о новом участнике группы и записываем данные в базу данных"""
    chat_id = message.chat.id  # Получаем ID чата
    chat_title = message.chat.title  # Получаем название чата
    user_id = message.new_chat_members[0].id  # Получаем ID пользователя, который зашел в группу
    username = message.new_chat_members[0].username  # Получаем username пользователя, который вступил в группу
    first_name = message.new_chat_members[0].first_name  # Получаем имя пользователя который вступил в группу
    last_name = message.new_chat_members[0].last_name  # Получаем фамилию пользователя который вступил в группу
    await bot.delete_message(chat_id, message.message_id)  # Удаляем сообщение о новом участнике группы
    name_table = "group_members_add"  # Имя таблицы в которую записываем данные
    writing_to_the_database_about_a_new_user(name_table, chat_id, chat_title, user_id, username, first_name, last_name,
                                             date_now)

@dp.message(F.content_type == ContentType.LEFT_CHAT_MEMBER)
async def deleting_a_message_about_a_member_has_left_the_group(message: Message):
    """Удаляем сообщение о покинувшем участнике группы и записываем данные в базу данных"""
    chat_id = message.chat.id  # Получаем ID чата с которого пользователь вышел
    chat_title = message.chat.title  # Получаем название с которого пользователь вышел
    user_id = message.left_chat_member.id  # Получаем ID пользователя, который вышел с чата
    username = message.left_chat_member.username  # Получаем username пользователя с которого пользователь вышел
    first_name = message.left_chat_member.first_name  # Получаем имя пользователя, того что вышел с группы
    last_name = message.left_chat_member.last_name  # Получаем фамилию пользователя, того что вышел с группы
    date_left = datetime.datetime.now()  # Дата выхода пользователя с группы
    await bot.delete_message(message.chat.id, message.message_id)  # Удаляем сообщение о покинувшем участнике группы
    name_table = "group_members_left"  # Имя таблицы в которую записываем данные
    writing_to_the_database_about_a_new_user(name_table, chat_id, chat_title, user_id, username, first_name, last_name,
                                             date_left)

@dp.message(F.content_type == ContentType.STICKER)
async def bot_message(message: Message, state: FSMContext) -> None:
    """Удаление стикеров"""
    # Если записанный id пользователя в боте записан, то сообщения пропускаются
    data_dict = reading_data_from_the_database()
    chat_id = message.chat.id
    user_id = message.from_user.id
    print(f"message.from_user.id: {user_id}")
    print(f"chat_id: {chat_id}, user_id: {user_id}")
    if (message.chat.id, message.from_user.id) in data_dict:
        print(f"{str(message.from_user.full_name)} отправил стикер в группу")
    else:
        await bot.delete_message(message.chat.id, message.message_id)  # Удаляем сообщение
        # Отправляем сообщение в группу
        warning = await message.answer(f"<code>✅ {str(message.from_user.full_name)}</code>\n"
                                       f"<code>В чате запрещено отправлять стикеры, для получения разрешения напишите "
                                       f"админу</code> ➡️ {username_admin}", parse_mode="HTML")
        await asyncio.sleep(int(time_del))  # Спим 20 секунд
        await warning.delete()  # Удаляем предупреждение от бота


def admin_handlers():
    """Регистрируем handlers для всех пользователей"""
    dp.register_message_handler(send_id, commands=['id'])
