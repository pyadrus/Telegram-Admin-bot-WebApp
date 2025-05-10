from fastapi import APIRouter
from loguru import logger

from utils.models import Group, GroupRestrictions

router = APIRouter()


@router.get("/api/get-chat-id")
async def get_chat_id(title: str):
    try:
        group = Group.get(Group.chat_title == title)
        return {"success": True, "chat_id": group.chat_id}
    except Group.DoesNotExist:
        return {"success": False, "error": "Группа не найдена"}


@router.get("/api/chat/require-subscription")
async def chat_subscribe(chat_title: str, required_chat_title: str):
    """
    Устанавливает ограничение на подписку для группы chat_title.
    Пользователи смогут писать только если подписаны на канал/группу required_chat_title.
    """
    try:
        # Получаем информацию о целевой группе (ту, которую хотим ограничить)
        group = Group.get(Group.chat_title == chat_title)
        group_id = group.chat_id
        logger.info(f"Первая группа {group_id}")

        # Получаем информацию о канале/группе, на который нужно подписаться
        required_group = Group.get(Group.chat_title == required_chat_title)
        channel_id = required_group.chat_id  # id канала или группы
        channel_username = required_group.chat_link  # username канала или группы
        logger.info(f"Вторая группа {channel_id}. Username {channel_username}")

        # Обновляем запись в базе
        restriction, created = GroupRestrictions.get_or_create(
            group_id=group_id,
            defaults={
                'required_channel_id': channel_id,
                'required_channel_username': channel_username
            }
        )
        if not created:
            # Если запись уже существует — обновляем её
            GroupRestrictions.update(
                required_channel_id=channel_id,
                required_channel_username=channel_username
            ).where(GroupRestrictions.group_id == group_id).execute()

        return {"success": True,
                "message": f"Теперь для группы '{chat_title}' требуется подписка на '{required_chat_title}'"}

    except Group.DoesNotExist as e:
        return {"success": False, "error": "Группа не найдена: " + str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}
