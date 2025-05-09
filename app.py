import uvicorn
from aiogram.types import ChatPermissions
from fastapi import FastAPI, Request
from fastapi import Form
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger

from system.dispatcher import bot
from utils.get_id import get_participants_count
from utils.models import Group, db

app = FastAPI()

# === Указываем директорию с шаблонами и статикой ===
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# === Права для чата ===
READ_ONLY = ChatPermissions(can_send_messages=False)  # Запрещено писать в чат
FULL_ACCESS = ChatPermissions(can_send_messages=True)  # Разрешено писать в чат


@app.get("/api/get-chat-id")
async def get_chat_id(title: str):
    try:
        group = Group.get(Group.chat_title == title)
        return {"success": True, "chat_id": group.chat_id}
    except Group.DoesNotExist:
        return {"success": False, "error": "Группа не найдена"}


@app.get("/api/chat/readonly")
async def chat_readonly(chat_id: int):
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


@app.get("/api/chat/writeable")
async def chat_writeable(chat_id: int):
    """
    Переводит чат в режим «все могут писать». Передаваемый chat_id, должен быть в формате -1001234567890, и являться
    числовым значением.
    """
    try:
        chat_id = str(f"-100{chat_id}")
        await bot.set_chat_permissions(chat_id=chat_id, permissions=FULL_ACCESS)
        return {"success": True, "message": "Чат переведён в режим «все могут писать»"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# === Маршруты ===

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Отображение стартовой страницы с приветствием пользователя.

    :param request: Объект запроса.
    :return: HTML-страница с приветствием.

    """
    return templates.TemplateResponse("index.html", {"request": request})


# Новый маршрут для "Формирование групп"
@app.get("/formation-groups")
async def formation_groups(request: Request):
    """
    Отображение страницы с формой для ввода username группы.

    :param request: Объект запроса.
    :return: HTML-страница с формой для ввода username группы.
    """
    return templates.TemplateResponse("formation_groups.html", {"request": request})


@app.post("/save-group")
async def save_group(chat_username: str = Form(...)):
    """
    Запись данных в базу данных по username группы.
    chat_id - ID группы,
    chat_title - название группы,
    chat_total - общее количество участников,
    chat_link - ссылка на группу.
    """
    try:
        chat_id, chat_title, chat_total, chat_link = await get_participants_count(chat_username)
        permission_to_write = "True"
        # Создаем таблицу, если она не создана ранее
        db.create_tables([Group], safe=True)
        with db.atomic():
            # Вставляем новую
            Group.insert(chat_id=chat_id, chat_title=chat_title, chat_total=chat_total, chat_link=chat_link,
                         permission_to_write=permission_to_write).execute()
        return RedirectResponse(url="/formation-groups?success=1", status_code=303)
    except Exception as e:
        return RedirectResponse(url="/formation-groups?error=1", status_code=303)


# Получение списка групп для отображения на странице
@app.get("/api/chat_title")
async def get_groups():
    """
    Получение списка групп, для отображения на странице пользователя количества участников. Отображается название
    группы с базы данных.
    """
    chat_title = list(Group.select().dicts())
    return {"chat_title": chat_title}


@app.get("/api/get-participants")
async def get_participants(chat_title: str):
    """
    Получение количества участников в группе.
    """
    try:
        group = Group.get(Group.chat_title == chat_title)
        # Здесь можно вызвать Telegram API для актуального числа участников
        return {"success": True, "participants_count": group.chat_total}
    except Group.DoesNotExist:
        return {"success": False, "error": "Группа не найдена"}


@app.get("/api/update-participants")
async def update_participants(chat_title: str):
    """
    Обновление количества участников в группе.
    """
    # Получаем запись из базы данных по chat_title
    try:
        group = Group.get(Group.chat_title == chat_title)

        # Получаем актуальные данные через Telegram
        chat_id, title, total, link = await get_participants_count(group.chat_link)
        # Обновляем запись в базе
        Group.update(chat_total=total).where(Group.chat_title == chat_title).execute()

        return {"success": True, "participants_count": total}
    except Group.DoesNotExist:
        return {"success": False, "error": "Группа не найдена"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# Получение списка групп для отображения на странице
@app.get("/api/chat_title_groups_select")
async def get_groups():
    """
    Получение списка групп, для отображения на странице пользователя количества участников. Отображается название
    группы с базы данных.
    """
    chat_title = list(Group.select().dicts())
    return {"chat_title": chat_title}


@app.get("/api/update-restrict-messages")
async def update_restrict_messages(chat_title: str, restricted: bool = True):
    """
    Обновление статуса блокировки сообщений в группе.  Если в группе "False", то блокировка сообщений включена. Если "True", то блокировка сообщений выключена.
    """
    try:
        group = Group.get(Group.chat_title == chat_title)
        permission_to_write = "False"
        # Обновляем запись в базе
        Group.update(permission_to_write=permission_to_write).where(Group.chat_title == chat_title).execute()
        return {"success": True, "permission_to_write": permission_to_write}
    except Group.DoesNotExist:
        return {"success": False, "error": "Группа не найдена"}
    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8080, reload=True)
