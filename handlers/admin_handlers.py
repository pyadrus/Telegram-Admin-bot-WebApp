import asyncio
import datetime
import io

from aiogram import types
from aiogram.dispatcher import FSMContext  # Определение состояний FSM
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode

from handlers.bot_handlers import username_admin
from messages.user_messages import info
from system.dispatcher import dp, bot, time_del
from system.sqlite import delete_bad_word
from system.sqlite import reading_bad_words_from_the_database
from system.sqlite import reading_data_from_the_database
from system.sqlite import reading_data_from_the_database_check
from system.sqlite import reading_from_the_database_of_forbidden_check_word
from system.sqlite import reading_from_the_database_of_forbidden_words
from system.sqlite import record_the_id_of_allowed_users
from system.sqlite import recording_actions_check_word_in_the_database
from system.sqlite import recording_actions_in_the_database
from system.sqlite import writing_bad_words_to_the_database
from system.sqlite import writing_check_words_to_the_database

date_now = datetime.datetime.now()


class AddUserStates(StatesGroup):
    WAITING_FOR_USER_ID = State()  # ожидание ввода ID пользователя;
    USER_ADDED = State()  # состояние, когда пользователь успешно добавлен в базу данных.


class AddAndDelBadWords(StatesGroup):
    """Создаем состояние для добавления плохих слов"""
    waiting_for_bad_word = State()
    waiting_for_check_word = State()
    del_for_bad_word = State()


@dp.message_handler(state=AddUserStates.USER_ADDED)
async def ignore_messages(message: types.Message):
    """Игнорирование сообщений, когда состояние FSM = USER_ADDED"""
    pass


@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message) -> None:
    """Отвечаем на команду /start"""
    await message.reply(info, parse_mode="HTML")


@dp.message_handler(commands=["help"])
async def help_handler(message: types.Message) -> None:
    """Отвечаем на команду /help"""
    await message.reply(info, parse_mode="HTML")


@dp.message_handler(commands=['id'])
async def send_id(message: types.Message):
    """Обработчик команды /id"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    print(f"Пользователь {user_id} вызвал команду '/id' в чате {chat_id}")
    # Проверяем, является ли пользователь админом в текущем чате
    chat_member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    print(chat_member)
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


@dp.message_handler(commands=['user_add'])
async def cmd_user_add(message: types.Message):
    """Обработчик команды /user_add. Команда /user_add используется для добавления новых пользователей в базу данных
    с определенными правами в группе"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    print(f"Пользователь {user_id} вызвал команду '/user_add' в чате {chat_id}")
    # Проверяем, является ли пользователь админом в текущем чате
    chat_member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    print(chat_member)
    if chat_member.status not in ["administrator", "creator"]:
        # Если пользователь не является админом, отправляем ему сообщение с предупреждением
        await bot.send_message(chat_id, "<code>✅ Команда доступна только для администраторов</code>", parse_mode="HTML")
        await message.delete()  # Удаляем сообщение с командой /user_add
        return
    # Если пользователь является админом, отправляем запрос на ввод ID пользователя
    await message.answer('Введите ID пользователя, для назначения особых прав в группе')
    # Переводим бота в состояние WAITING_FOR_USER_ID
    await AddUserStates.WAITING_FOR_USER_ID.set()
    await message.delete()  # Удаляем сообщение с командой /user_add


@dp.message_handler(state=AddUserStates.WAITING_FOR_USER_ID)
async def process_user_id(message: types.Message, state: FSMContext):
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
        await state.finish()  # Сбрасываем состояние FSM
    except ValueError:
        # Если введенный пользователем текст не может быть преобразован в число отправляем сообщение об ошибке
        await message.answer('Введите целое число')
        await message.delete()  # Удаляем сообщение с неправильным вводом


async def check_root(message: types.Message):
    for admin in (await bot.get_chat_administrators(chat_id=message.chat.id)):
        if admin["user"]["id"] == message.from_user.id:
            return True
    return False


async def update(message: types.Message):
    member_id_username = dict()
    member_username_id = dict()
    member_username_id.setdefault(message.chat.id, dict())
    member_id_username.setdefault(message.chat.id, dict())

    member_id_username[message.chat.id][
        message.from_user.id] = '@' + message.from_user.username if message.from_user.username is not None else ''
    member_username_id[message.chat.id][
        '@' + message.from_user.username if message.from_user.username is not None else ''] = message.from_user.id

    for member in message.new_chat_members:
        member_username_id.setdefault(message.chat.id, dict())
        member_id_username.setdefault(message.chat.id, dict())

        member_id_username[message.chat.id][member.id] = '@' + member.username if member.username is not None else ''
        member_username_id[message.chat.id]['@' + member.username if member.username is not None else ''] = member.id


@dp.message_handler(commands="pin")
async def pin(message: types.Message):
    """Обработчик команды /pin"""
    if message.from_user.id != message.chat.id:
        if await check_root(message):
            try:
                await bot.pin_chat_message(chat_id=message.chat.id, message_id=message.reply_to_message.message_id)
            except:
                await message.answer('Напишите /pin в виде ответа на сообщение, которое хотите закрепить')
        else:
            await update(message)
            await message.delete()
    else:
        await message.answer('Бот реагирует только на сообщения в чате, но не в личку')


@dp.message_handler(commands="unpin")
async def unpin(message: types.Message):
    """Обработчик команды /unpin"""
    if message.from_user.id != message.chat.id:
        if await check_root(message):
            try:
                await bot.unpin_chat_message(chat_id=message.chat.id, message_id=message.reply_to_message.message_id)
            except:
                await message.answer('Напишите /unpin в виде ответа на сообщение, которое хотите открепить')
        else:
            await update(message)
            await message.delete()
    else:
        await message.answer('Бот реагирует только на сообщения в чате, но не в личку')


@dp.message_handler(commands="unpin_all")
async def unpin_all(message: types.Message):
    """Обработчик команды /unpin_all"""
    # Проверка того, была ли команда вызвана из личных сообщений или в чате
    if message.from_user.id != message.chat.id:
        # Проверка того, является ли вызывающий команду пользователь администратором чата.
        if await check_root(message):
            try:
                # Удаление всех закрепленных сообщений в чате.
                await bot.unpin_all_chat_messages(chat_id=message.chat.id)
            except:
                # Обновление сообщения (удаление команды) в случае, если вызывающий команду пользователь не является
                # администратором.
                await message.answer('Нет закрепленных сообщений')
        else:
            # Обновление сообщения (удаление команды) в случае, если вызывающий команду пользователь не является
            # администратором.
            await update(message)
            # Удаление сообщения с командой /unpin_all в случае, если вызывающий команду пользователь не является
            # администратором.
            await message.delete()
    else:
        # Отправка сообщения о том, что в чате нет закрепленных сообщений, в случае, если закрепленных сообщений нет.
        await message.answer('Бот реагирует только на сообщения в чате, но не в личку')


@dp.message_handler(commands=['add_bad'])
async def cmd_add_bad(message: types.Message):
    """Обработчик команды /add_bad"""
    # Проверяем, вызвал ли команду админ чата
    chat_member = await bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
    if not chat_member.is_chat_admin():
        await message.reply('Эту команду может использовать только администратор чата.')
        return
    await message.answer('✒️ Введите слово, которое нужно добавить ➕ в список 📝 плохих слов 🤬: ',
                         parse_mode=ParseMode.HTML)
    await AddAndDelBadWords.waiting_for_bad_word.set()  # Переходим в состояние ожидания плохого слова


@dp.message_handler(commands=['add_check'])
async def cmd_add_check(message: types.Message):
    """Обработчик команды /add_check"""
    # Получаем информацию о пользователе
    user = await bot.get_chat_member(message.chat.id, message.from_user.id)
    # Проверяем, является ли пользователь администратором чата
    if user.status in ("administrator", "creator"):
        await message.answer('✒️  Введите check слово, которое нужно добавить в список check слов:')
        await AddAndDelBadWords.waiting_for_check_word.set()  # Переходим в состояние ожидания плохого слова
    else:
        # Отправляем сообщение о том, что пользователь не является администратором чата
        await message.reply("Команда доступна только администраторам чата.")


@dp.message_handler(commands=['del_bad'])
async def delete_bad_handler(message: types.Message):
    """Обработчик команды /del_bad"""
    # Проверяем, вызвал ли команду админ чата
    chat_member = await bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
    if not chat_member.is_chat_admin():
        await message.reply('Эту команду может использовать только администратор чата.')
        return
    await message.answer('✒️ Введите слово, которое нужно удалить из базы данных:')
    await AddAndDelBadWords.del_for_bad_word.set()  # Переходим в состояние ожидания плохого слова


@dp.message_handler(commands=['del_check'])
async def delete_check_handler(message: types.Message):
    """Обработчик команды /del_check"""
    # Проверяем, вызвал ли команду админ чата
    chat_member = await bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
    if not chat_member.is_chat_admin():
        await message.reply('Эту команду может использовать только администратор чата.')
        return
    await message.answer('✒️ Введите check слово, которое нужно удалить из базы данных:')
    await AddAndDelBadWords.del_for_bad_word.set()  # Переходим в состояние ожидания плохого слова


@dp.message_handler(commands=["get_data_bad"])
async def get_data(message: types.Message):
    """Команда для получения данных из базы данных с помощью команды /get_data"""
    # Получаем информацию о пользователе
    user = await bot.get_chat_member(message.chat.id, message.from_user.id)
    # Проверяем, является ли пользователь администратором чата
    if user.status in ("administrator", "creator"):
        # Получаем данные из базы данных
        data = await reading_data_from_the_database()
        # Создаем файл в памяти
        output = io.StringIO()
        # Записываем данные в файл
        for row in data:
            output.write(str(row) + "\n")
        # Отправляем файл пользователю в личку
        output.seek(0)
        await bot.send_document(message.from_user.id, types.InputFile(output, filename="data_bad.txt"))
        # Отправляем сообщение с результатом в личку пользователю
        await bot.send_message(message.from_user.id, "Данные успешно отправлены вам в личку.")
    else:
        # Отправляем сообщение о том, что пользователь не является администратором чата
        await message.reply("Команда доступна только администраторам чата.")


@dp.message_handler(commands=["get_data_check"])
async def get_data_check(message: types.Message):
    """Команда для получения данных из базы данных с помощью команды /get_data_check"""
    # Получаем информацию о пользователе
    user = await bot.get_chat_member(message.chat.id, message.from_user.id)
    # Проверяем, является ли пользователь администратором чата
    if user.status in ("administrator", "creator"):
        # Получаем данные из базы данных
        data = await reading_data_from_the_database_check()
        # Создаем файл в памяти
        output = io.StringIO()
        # Записываем данные в файл
        for row in data:
            output.write(str(row) + "\n")
        # Отправляем файл пользователю в личку
        output.seek(0)
        await bot.send_document(message.from_user.id, types.InputFile(output, filename="data_check.txt"))
        # Отправляем сообщение с результатом в личку пользователю
        await bot.send_message(message.from_user.id, "Данные успешно отправлены вам в личку.")
    else:
        # Отправляем сообщение о том, что пользователь не является администратором чата
        await message.reply("Команда доступна только администраторам чата.")


@dp.message_handler(commands=["get_bad_words"])
async def get_bad_words(message: types.Message):
    """Команда для получения списка запрещенных слов /get_bad_words"""
    user = await bot.get_chat_member(message.chat.id, message.from_user.id)
    # Проверяем, является ли пользователь администратором чата
    if user.status in ("administrator", "creator"):
        bad_words = await reading_bad_words_from_the_database()
        output = io.StringIO()
        for word in bad_words:
            output.write(word + "\n")
        output.seek(0)
        await bot.send_document(message.from_user.id, types.InputFile(output, filename="bad_words.txt"))
    else:
        await message.answer("Вы должны быть администратором чата, чтобы получить список запрещенных слов.")


@dp.message_handler(state=AddAndDelBadWords.waiting_for_bad_word)
async def process_bad_word(message: types.Message, state: FSMContext):
    """Обработчик текстовых сообщений в состоянии ожидания плохого слова"""
    bad_word = message.text.strip().lower()  # Получаем слово от пользователя
    user_id = message.from_user.id  # Получаем ID пользователя
    username = message.from_user.username  # Получаем username пользователя
    user_full_name = message.from_user.full_name  # Получаем Ф.И. пользователя
    chat_id = message.chat.id  # Получаем ID чата / канала
    chat_title = message.chat.title  # Получаем название чата / канала
    await writing_bad_words_to_the_database(bad_word, user_id, username, user_full_name, chat_id,
                                            chat_title)  # Запись запрещенных слов в базу данных
    # Выводим сообщение об успешном добавлении слова
    await message.reply('✅ Слово успешно добавлено ➕ в список плохих слов 🤬.', parse_mode=ParseMode.HTML)
    await state.finish()  # Сбрасываем состояние


@dp.message_handler(state=AddAndDelBadWords.del_for_bad_word)
async def process_bad_word(message: types.Message, state: FSMContext):
    """Обработчик текстовых сообщений в состоянии ожидания плохого слова"""
    bad_word = message.text.strip().lower()  # Получаем слово от пользователя
    await delete_bad_word(bad_word)
    # Выводим сообщение об успешном удалении слова
    await message.reply('Слово успешно удалено ➖ из списка плохих слов 🤬.', parse_mode=ParseMode.HTML)
    await state.finish()  # Сбрасываем состояние


@dp.message_handler(state=AddAndDelBadWords.waiting_for_check_word)
async def process_check_word(message: types.Message, state: FSMContext):
    """Обработчик текстовых сообщений в состоянии ожидания плохого слова"""
    bad_word = message.text.strip().lower()  # Получаем слово от пользователя
    user_id = message.from_user.id  # Получаем ID пользователя
    username = message.from_user.username  # Получаем username пользователя
    user_full_name = message.from_user.full_name  # Получаем Ф.И. пользователя
    chat_id = message.chat.id  # Получаем ID чата / канала
    chat_title = message.chat.title  # Получаем название чата / канала
    await writing_check_words_to_the_database(bad_word, user_id, username, user_full_name, chat_id,
                                              chat_title)  # Запись запрещенных слов в базу данных
    # Выводим сообщение об успешном добавлении слова
    await message.reply('✅ Слово успешно добавлено ➕ в список check слов.', parse_mode=ParseMode.HTML)
    await state.finish()  # Сбрасываем состояние


@dp.message_handler()
async def process_message(message: types.Message):
    """Обрабатываем сообщения от пользователей, проверяем наличие запрещенных слов в сообщении"""
    bad_words = await reading_from_the_database_of_forbidden_words()
    for word in bad_words:
        if word[0] in message.text.lower():
            await recording_actions_in_the_database(word[0], message)
            await message.delete()  # Удаляем сообщение от пользователя с запрещенным словом
            warning = await bot.send_message(message.chat.id, f'В вашем сообщении обнаружено запрещенное слово. '
                                                              f'Пожалуйста, не используйте его в дальнейшем.')
            await asyncio.sleep(int(time_del))  # Спим 20 секунд
            await warning.delete()  # Удаляем предупреждение от бота

    # Проверяем наличие запрещенных слов для проверки в сообщении
    check_words = await reading_from_the_database_of_forbidden_check_word()
    for check_word in check_words:
        if check_word[0] in message.text.lower():
            await recording_actions_check_word_in_the_database(check_word[0], message)


def admin_handlers():
    """Регистрируем handlers для всех пользователей"""
    dp.register_message_handler(send_id)
    dp.register_message_handler(cmd_user_add)
    dp.register_message_handler(send_welcome)
    dp.register_message_handler(help_handler)
    dp.register_message_handler(pin)
    dp.register_message_handler(unpin)
    dp.register_message_handler(unpin_all)
    dp.register_message_handler(cmd_add_check)  # Команда /add_check
    dp.register_message_handler(cmd_add_bad)  # Команда /add_bad
    dp.register_message_handler(send_welcome)  # Команда /start
    dp.register_message_handler(delete_bad_handler)  # Команда /del_bad
    dp.register_message_handler(get_data)  # Команда /get_data
    dp.register_message_handler(get_bad_words)  # Команда /get_bad_words
    dp.register_message_handler(get_data_check)  # Команда /get_data_check
    dp.register_message_handler(delete_check_handler)  # Команда /del_check
