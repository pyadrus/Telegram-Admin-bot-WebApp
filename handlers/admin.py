import datetime

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loguru import logger

from states.states import AddUserStates
from system.dispatcher import bot
from system.dispatcher import router
from utils.models import PrivilegedUsers


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
        chat_member_write = PrivilegedUsers(
            chat_id=message.chat.id,  # Получаем ID чата
            user_id=int(message.text),  # Получаем введенный админом ID
            username=chat_member.user.username if chat_member.user.username else "",
            first_name=chat_member.user.first_name if chat_member.user.first_name else "",
            last_name=chat_member.user.last_name if chat_member.user.last_name else "",
            date_add=datetime.datetime.now(),
            admin_id=message.from_user.id,  # Получаем ID админа, который отправил сообщение с ID боту
            chat_title=message.chat.title  # Получаем название чата
        )
        chat_member_write.save()

        # Отправляем сообщение об успешной записи в чат
        await message.answer(
            f"<code>✅ Участнику {chat_member.user.first_name} {chat_member.user.last_name} даны особые права в группе</code>",
            parse_mode="HTML")
        await message.delete()  # Удаляем сообщение с введенным ID пользователя
        await state.clear()  # Сбрасываем состояние FSM
    except ValueError:
        # Если введенный пользователем текст не может быть преобразован в число отправляем сообщение об ошибке
        await message.answer('Введите целое число')
        await message.delete()  # Удаляем сообщение с неправильным вводом


def register_admin_handlers():
    """Регистрируем handlers для всех пользователей"""
    router.message.register(cmd_user_add)
