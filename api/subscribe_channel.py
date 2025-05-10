from fastapi import APIRouter

from system.dispatcher import bot, READ_ONLY
from utils.models import Group

router = APIRouter()


@router.get("/api/get-chat-id")
async def get_chat_id(title: str):
    try:
        group = Group.get(Group.chat_title == title)
        return {"success": True, "chat_id": group.chat_id}
    except Group.DoesNotExist:
        return {"success": False, "error": "Группа не найдена"}


@router.get("/api/chat/subscribe")
async def chat_subscribe(chat_id: int):
    """
    Переводит чат в режим «только чтение». Передаваемый chat_id, должен быть в формате -1001234567890, и являться
    числовым значением.
    """
    try:
        chat_id = str(f"-100{chat_id}")
        await bot.set_chat_permissions(chat_id=int(chat_id), permissions=READ_ONLY)
        return {"success": True, "message": "Чат переведён в режим «только чтение»"}
    except Exception as e:
        return {"success": False, "error": str(e)}
