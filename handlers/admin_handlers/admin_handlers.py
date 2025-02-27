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
    logger.info(f"Пользователь {message.from_user.id} вызвал команду '/id' в чате {message.chat.id}")
    # Проверяем, является ли пользователь админом в текущем чате
    chat_member = await bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
    if chat_member.status not in ["administrator", "creator"]:
        # Если пользователь не является админом, отправляем ему сообщение с предупреждением
        await bot.send_message(message.chat.id, "Команда доступна только для администраторов.")
        await message.delete()  # Удаляем сообщение с командой /id
        return
    try:
        # получаем ID пользователя, который написал сообщение
        # получаем информацию о пользователе по его ID
        user = await bot.get_chat(message.reply_to_message.from_user.id)
        # отправляем ID, имя и фамилию пользователя в личку
        await bot.send_message(chat_id=message.from_user.id,
                               text=f'Пользователь: {user.first_name} {user.last_name}\nID: {user.id}')
        # удаляем сообщение с командой /id
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except AttributeError:
        # если произошла ошибка AttributeError, то сообщаем об этом пользователю
        await bot.send_message(chat_id=message.chat.id, text='Ответьте на сообщение пользователя, чтобы узнать его ID')


@router.message(Command("user_add"))
async def cmd_user_add(message: Message, state: FSMContext):
    """
    Обработчик команды /user_add. Команда /user_add используется для добавления новых пользователей в базу данных
    с определенными правами в группе
    """
    logger.info(f"Пользователь {message.from_user.id} вызвал команду '/user_add' в чате {message.chat.id}")
    # Проверяем, является ли пользователь админом в текущем чате
    chat_member = await bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)
    if chat_member.status not in ["administrator", "creator"]:
        # Если пользователь не является админом, отправляем ему сообщение с предупреждением
        await bot.send_message(message.chat.id, "<code>✅ Команда доступна только для администраторов</code>",
                               parse_mode="HTML")
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
        chat_member = await bot.get_chat_member(message.chat.id, int(message.text))
        record_the_id_of_allowed_users(
            chat_id=message.chat.id,  # Получаем ID чата
            user_id=int(message.text),  # Получаем введенный админом ID
            username=chat_member.user.username if chat_member.user.username else "",
            first_name=chat_member.user.first_name if chat_member.user.first_name else "",
            last_name=chat_member.user.last_name if chat_member.user.last_name else "",
            date_add=datetime.datetime.now(),
            admin_id=message.from_user.id,  # Получаем ID админа, который отправил сообщение с ID боту
            chat_title=message.chat.title  # Получаем название чата
        )  # Записываем данные
        # Отправляем сообщение об успешной записи в чат
        await message.answer(
            f"<code>✅ Участнику {chat_member.user.first_name if chat_member.user.first_name else ""} {chat_member.user.last_name if chat_member.user.last_name else ""} "
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
    if message.from_user.id == 535185511:  # ID администратора
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
    writing_bad_words_to_the_database(
        bad_word=message.text.strip().lower(),  # Получаем слово от пользователя
        user_id=message.from_user.id,  # Получаем ID пользователя
        username=message.from_user.username,  # Получаем username пользователя
        user_full_name=message.from_user.full_name,  # Получаем Ф.И. пользователя
        chat_id=message.chat.id,  # Получаем ID чата / канала
        chat_title=message.chat.title  # Получаем название чата / канала
    )  # Запись запрещенных слов в базу данных
    # Выводим сообщение об успешном добавлении слова
    await message.reply('✅ Слово успешно добавлено ➕ в список плохих слов 🤬.', parse_mode="HTML")
    await state.clear()  # Сбрасываем состояние

import sqlite3
import asyncio
from aiogram.enums import ChatMemberStatus
from aiogram.filters import Command
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, JOIN_TRANSITION
from aiogram.types import Message, ChatMemberUpdated
from loguru import logger

from system.dispatcher import bot
from system.dispatcher import router
from system.sqlite import path_database

async def delete_message_after_delay(message: Message, delay: int):
    """Удаляет сообщение через заданное количество секунд"""
    await asyncio.sleep(delay)
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception as e:
        logger.error(f"Ошибка при удалении сообщения: {e}")

@router.message(Command("setchannel"))
async def set_channel(message: Message):
    """Обработчик команды /setchannel"""
    logger.info(f"Пользователь {message.from_user.id} вызвал команду '/setchannel' в чате {message.chat.id}")
    if message.chat.type not in ['group', 'supergroup']:
        await message.reply("Эта команда работает только в группах!")
        return

    chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if chat_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
        await message.reply("Только администраторы могут использовать эту команду!")
        return

    try:
        args = message.text.split()
        if len(args) != 2 or not args[1].startswith('@'):
            await message.reply("Используйте: /setchannel @username (например, @vkysno_i_prossto)")
            return

        channel_username = args[1]
        # Получаем информацию о канале по username
        chat = await bot.get_chat(channel_username)
        channel_id = chat.id

        conn = sqlite3.connect(path_database)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS group_restrictions
                             (group_id INTEGER PRIMARY KEY, required_channel_id INTEGER, required_channel_username TEXT)''')
        c.execute('INSERT OR REPLACE INTO group_restrictions (group_id, required_channel_id, required_channel_username) VALUES (?, ?, ?)',
                  (message.chat.id, channel_id, channel_username))
        conn.commit()
        conn.close()

        await message.reply(f"Установлен канал {channel_username} для обязательной подписки")

    except Exception as e:
        await message.reply(f"Ошибка: {str(e)}. Убедитесь, что username канала верный и бот имеет к нему доступ")

@router.message()
async def check_subscription(message: Message):
    if message.chat.type not in ['group', 'supergroup']:
        return

    try:
        conn = sqlite3.connect(path_database)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS group_restrictions
                                     (group_id INTEGER PRIMARY KEY, required_channel_id INTEGER, required_channel_username TEXT)''')
        c.execute('SELECT required_channel_id, required_channel_username FROM group_restrictions WHERE group_id = ?', (message.chat.id,))
        result = c.fetchone()
        conn.close()

        if not result:
            return

        required_channel_id, required_channel_username = result

        member = await bot.get_chat_member(required_channel_id, message.from_user.id)
        if member.status not in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
            await message.delete()
            # Отправляем сообщение и сохраняем его объект
            bot_message = await message.answer(
                f"{message.from_user.mention_html()}, привет! 👋 Чтобы наша группа оставалась уютной и свободной от спама, пожалуйста, подпишись на канал {required_channel_username} — это поможет нам убедиться, что ты не бот. 🤖 Подписка нужна только для того, чтобы писать здесь, и это временная мера. Спасибо, за понимание! 🌟",
                parse_mode="HTML"
            )
            # Запускаем задачу удаления сообщения через 60 секунд
            asyncio.create_task(delete_message_after_delay(bot_message, 60))
    except Exception as e:
        logger.error(f"Ошибка при проверке подписки: {e}")
        await message.delete()
        user_mention = message.from_user.mention_html() if message.from_user.username else f"User {message.from_user.id}"
        # Используем username из базы или ID, если username недоступен
        conn = sqlite3.connect(path_database)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS group_restrictions
                                     (group_id INTEGER PRIMARY KEY, required_channel_id INTEGER, required_channel_username TEXT)''')
        c.execute('SELECT required_channel_username FROM group_restrictions WHERE group_id = ?', (message.chat.id,))
        result = c.fetchone()
        conn.close()
        channel_username = result[0] if result else "неизвестный канал"
        # Отправляем сообщение и сохраняем его объект
        bot_message = await message.answer(
            f"{user_mention}, привет! 👋 Чтобы наша группа оставалась уютной и свободной от спама, пожалуйста, подпишись на канал {channel_username} — это поможет нам убедиться, что ты не бот. 🤖 Подписка нужна только для того, чтобы писать здесь, и это временная мера. Спасибо, за понимание! 🌟",
            parse_mode="HTML"
        )
        # Запускаем задачу удаления сообщения через 60 секунд
        asyncio.create_task(delete_message_after_delay(bot_message, 60))

@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def on_chat_member_update(update: ChatMemberUpdated):
    if update.new_chat_member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR]:
        try:
            conn = sqlite3.connect(path_database)
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS group_restrictions
                                         (group_id INTEGER PRIMARY KEY, required_channel_id INTEGER, required_channel_username TEXT)''')
            c.execute('SELECT group_id FROM group_restrictions WHERE required_channel_id = ?', (update.chat.id,))
            groups = c.fetchall()
            conn.close()

            for group in groups:
                try:
                    member = await bot.get_chat_member(group[0], update.user.id)
                    if member.status == ChatMemberStatus.RESTRICTED:
                        await bot.restrict_chat_member(
                            group[0],
                            update.user.id,
                            can_send_messages=True
                        )
                except Exception as e:
                    logger.error(f"Ошибка при снятии ограничений для группы {group[0]}: {e}")
                    continue
        except sqlite3.Error as e:
            logger.error(f"Ошибка базы данных при обработке подписки: {e}")


def register_admin_handlers():
    """Регистрируем handlers для всех пользователей"""
    router.message.register(cmd_add_bad)
    router.message.register(cmd_user_add)
    router.message.register(set_channel)


if __name__ == '__main__':
    register_admin_handlers()
