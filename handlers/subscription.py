import asyncio

from aiogram.enums import ChatMemberStatus
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, JOIN_TRANSITION
from aiogram.types import Message, ChatMemberUpdated, ChatPermissions
from loguru import logger

from system.dispatcher import bot
from system.dispatcher import router
from utils.models import GroupRestrictions


@router.message()
async def check_subscription(message: Message):
    """Проверки подписки на группу / канал"""
    if message.chat.type not in ['group', 'supergroup']:
        return
    try:
        clean_id = str(message.chat.id)[4:]  # Преобразуем в строку и убираем первые 4 символа (-100)
        restriction = GroupRestrictions.get(GroupRestrictions.group_id == clean_id)
        if not restriction:
            return
        required_channel_id = restriction.required_channel_id
        required_channel_username = restriction.required_channel_username
        chat_id = str(f"-100{required_channel_id}")
        member = await bot.get_chat_member(chat_id=chat_id, user_id=message.from_user.id)
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
        clean_id = str(message.chat.id)[4:]  # Преобразуем в строку и убираем первые 4 символа (-100)
        restriction = GroupRestrictions.get(GroupRestrictions.group_id == clean_id)
        channel_username = restriction.required_channel_username
        # Отправляем сообщение и сохраняем его объект
        bot_message = await message.answer(
            f"{user_mention}, привет! 👋 Чтобы наша группа оставалась уютной и свободной от спама, пожалуйста, подпишись на канал {channel_username} — это поможет нам убедиться, что ты не бот. 🤖 Подписка нужна только для того, чтобы писать здесь, и это временная мера. Спасибо, за понимание! 🌟",
            parse_mode="HTML")
        # Запускаем задачу удаления сообщения через 60 секунд
        asyncio.create_task(delete_message_after_delay(bot_message, 60))


@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def on_chat_member_update(update: ChatMemberUpdated):
    """Снимает ограничения с пользователя, если он подписался на канал"""
    if update.new_chat_member.status not in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR]:
        return
    try:
        # Чистим ID канала от префикса -100 перед поиском в базе
        clean_channel_id = str(update.chat.id)[4:]  # -> "2022404388"
        # Находим все группы, где требуется подписка на этот канал
        query = GroupRestrictions.select(GroupRestrictions.group_id).where(
            GroupRestrictions.required_channel_id == clean_channel_id
        )
        # Получаем список ID групп
        groups = list(query.tuples())
        for group_tuple in groups:
            group_id = group_tuple[0]  # Получаем group_id из кортежа (предполагается, что select вернул один столбец)
            try:
                member = await bot.get_chat_member(chat_id=group_id, user_id=update.user.id)
                if member.status == ChatMemberStatus.RESTRICTED:
                    await bot.restrict_chat_member(
                        chat_id=group_id,
                        user_id=update.user.id,
                        permissions=ChatPermissions(can_send_messages=True)
                    )
                    logger.info(f"Пользователь {update.user.id} разблокирован в группе {group_id}")
            except Exception as e:
                logger.error(f"Ошибка при снятии ограничений для группы {group_id}: {e}")
                continue
    except Exception as e:
        logger.error(f"Ошибка при обработке события JOIN_TRANSITION: {e}")


async def delete_message_after_delay(message: Message, delay: int):
    """Удаляет сообщение через заданное количество секунд"""
    await asyncio.sleep(delay)
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except Exception as e:
        logger.error(f"Ошибка при удалении сообщения: {e}")


def register_subscription_handlers():
    router.message.register(check_subscription)
    router.message.register(on_chat_member_update)
