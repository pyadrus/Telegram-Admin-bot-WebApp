import datetime

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loguru import logger

from states.states import AddAndDelBadWords, AddUserStates
from system.dispatcher import bot
from system.dispatcher import router
from system.sqlite import writing_bad_words_to_the_database, record_the_id_of_allowed_users


@router.message(Command("id"))
async def send_id(message: Message):
    """Обработчик команды /id"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} вызвал команду '/id' в чате {chat_id}")
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


@router.message(Command("user_add"))
async def cmd_user_add(message: Message, state: FSMContext):
    """Обработчик команды /user_add. Команда /user_add используется для добавления новых пользователей в базу данных
    с определенными правами в группе"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} вызвал команду '/user_add' в чате {chat_id}")
    # Проверяем, является ли пользователь админом в текущем чате
    chat_member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    if chat_member.status not in ["administrator", "creator"]:
        # Если пользователь не является админом, отправляем ему сообщение с предупреждением
        await bot.send_message(chat_id, "<code>✅ Команда доступна только для администраторов</code>", parse_mode="HTML")
        await message.delete()  # Удаляем сообщение с командой /user_add
        return
    # Если пользователь является админом, отправляем запрос на ввод ID пользователя
    await message.answer('Введите ID пользователя, для назначения особых прав в группе')
    await state.set_state(AddUserStates.WAITING_FOR_USER_ID)  # Переводим бота в состояние WAITING_FOR_USER_ID
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
                                       last_name, datetime.datetime.now(), admin_id, chat_title)  # Записываем данные
        # Отправляем сообщение об успешной записи в чат
        await message.answer(f"<code>✅ Участнику {first_name} {last_name} "
                             f"даны особые права в группе</code>", parse_mode="HTML")
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
    admin_id = 535185511  # ID администратора

    if message.from_user.id == admin_id:
        await message.answer(
            '✒️ Введите слово, которое нужно добавить ➕ в список 📝 плохих слов 🤬: ',
            parse_mode="HTML"
        )
        await state.set_state(AddAndDelBadWords.waiting_for_bad_word)  # Переходим в состояние ожидания плохого слова
    else:
        await message.reply('Эту команду может использовать только администратор бота.')


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


def register_admin_handlers():
    """Регистрируем handlers для всех пользователей"""
    router.message.register(cmd_add_bad)
    router.message.register(cmd_user_add)


if __name__ == '__main__':
    register_admin_handlers()
