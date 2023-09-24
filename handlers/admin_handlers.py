import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext  # Определение состояний FSM
from aiogram.dispatcher.filters.state import State, StatesGroup

from system.dispatcher import dp, bot
from system.sqlite import record_the_id_of_allowed_users

date_now = datetime.datetime.now()


class AddUserStates(StatesGroup):
    WAITING_FOR_USER_ID = State()  # ожидание ввода ID пользователя;
    USER_ADDED = State()  # состояние, когда пользователь успешно добавлен в базу данных.


# Игнорирование сообщений, когда состояние FSM = USER_ADDED
@dp.message_handler(state=AddUserStates.USER_ADDED)
async def ignore_messages(message: types.Message):
    pass


info = '''
<b>✅ Основные команды бота:</b>
<u>/start</u>     – 🤖 запустить бота,
<u>/help</u>      – 🤖 информация по работе с ботом,
<u>/id</u>        – 🧾 узнать ID участника чата (использование в виде ответа на сообщение),
<u>/user_add</u>  – 🧾 дать пользователю определенные права в группе (нужен ID участника),
<u>/pin</u>       – 📌 закрепить сообщение (использование в виде ответа на сообщение, которое хотите закрепить),
<u>/unpin</u>     – 📌 открепить сообщение (использование в виде ответа на сообщение, которое хотите открепить),
<u>/unpin_all</u> – 📌 открепить все закрепленные сообщения,
<u>@PyAdminRUS</u>– 🔗 связь с администратором (разработчиком).
'''


# обработчик команды /start
@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message) -> None:
    """Отвечаем на команду start"""
    await message.reply(info, parse_mode="HTML")


# обработчик команды /help
@dp.message_handler(commands=["help"])
async def help_handler(message: types.Message) -> None:
    """Отвечаем на команду help"""
    await message.reply(info, parse_mode="HTML")


# обработчик команды /id
@dp.message_handler(commands=['id'])
async def send_id(message: types.Message):
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


# Обработчик команды /user_add
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


# Обработчик ввода ID пользователя
@dp.message_handler(state=AddUserStates.WAITING_FOR_USER_ID)
async def process_user_id(message: types.Message, state: FSMContext):
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
        """
        Стиль текста для parse_mode="HTML", <code> - моноширинный, <b> - жирный, <i> - наклонный
        """
        # Отправляем сообщение об успешной записи в чат
        await message.answer(f"<code>✅ Участнику {first_name} {last_name} "
                             f"даны особые права в группе</code> ➡️ @PyAdminRUS", parse_mode="HTML")
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


# Обработчик команды /pin
@dp.message_handler(commands="pin")
async def pin(message: types.Message):
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


# Обработчик команды /unpin
@dp.message_handler(commands="unpin")
async def unpin(message: types.Message):
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


# Обработчик команды /unpin_all
@dp.message_handler(commands="unpin_all")
async def unpin_all(message: types.Message):
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


def admin_handlers():
    """Регистрируем handlers для всех пользователей"""
    dp.register_message_handler(send_id)
    dp.register_message_handler(cmd_user_add)
    dp.register_message_handler(send_welcome)
    dp.register_message_handler(help_handler)
    dp.register_message_handler(pin)
    dp.register_message_handler(unpin)
    dp.register_message_handler(unpin_all)
