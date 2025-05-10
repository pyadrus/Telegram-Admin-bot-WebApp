import asyncio

from aiogram.enums import ChatMemberStatus
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, JOIN_TRANSITION
from aiogram.types import Message, ChatMemberUpdated
from loguru import logger

from handlers.admin.admin import delete_message_after_delay
from system.dispatcher import bot
from system.dispatcher import router
from utils.models import get_required_channel_for_group, get_required_channel_username_for_group, \
    get_groups_by_channel_id


@router.message()
async def check_subscription(message: Message):
    """Проверки подписки на группу / канал"""
    if message.chat.type not in ['group', 'supergroup']:
        return
    try:
        result = get_required_channel_for_group(message)
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
        result = get_required_channel_username_for_group(message)
        channel_username = result[0] if result else "неизвестный канал"
        # Отправляем сообщение и сохраняем его объект
        bot_message = await message.answer(
            f"{user_mention}, привет! 👋 Чтобы наша группа оставалась уютной и свободной от спама, пожалуйста, подпишись на канал {channel_username} — это поможет нам убедиться, что ты не бот. 🤖 Подписка нужна только для того, чтобы писать здесь, и это временная мера. Спасибо, за понимание! 🌟",
            parse_mode="HTML")
        # Запускаем задачу удаления сообщения через 60 секунд
        asyncio.create_task(delete_message_after_delay(bot_message, 60))


@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def on_chat_member_update(update: ChatMemberUpdated):
    if update.new_chat_member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR]:
        groups = get_groups_by_channel_id(update)
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


def register_subscription_handlers():
    router.message.register(check_subscription)
    router.message.register(on_chat_member_update)
