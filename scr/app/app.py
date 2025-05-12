from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi import Form
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger

from scr.bot.system.dispatcher import bot, READ_ONLY, FULL_ACCESS
from scr.utils.get_id import get_participants_count
from scr.utils.models import BadWords, PrivilegedUsers
from scr.utils.models import Group, db
from scr.utils.models import GroupRestrictions

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# === Подключаем шаблоны и статику ===
app.mount("/scr/app/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


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
@app.get("/chat_title")
async def get_groups():
    """
    Получение списка групп, для отображения на странице пользователя количества участников. Отображается название
    группы с базы данных.
    """
    chat_title = list(Group.select().dicts())
    return {"chat_title": chat_title}


@app.get("/get-participants")
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


@app.get("/update-participants")
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
        Group.update(chat_total=total).where(
            Group.chat_title == chat_title).execute()

        return {"success": True, "participants_count": total}
    except Group.DoesNotExist:
        return {"success": False, "error": "Группа не найдена"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# Получение списка групп для отображения на странице
@app.get("/chat_title_groups_select")
async def get_groups():
    """
    Получение списка групп, для отображения на странице пользователя количества участников. Отображается название
    группы с базы данных.
    """
    chat_title = list(Group.select().dicts())
    return {"chat_title": chat_title}


@app.get("/update-restrict-messages")
async def update_restrict_messages(chat_title: str, restricted: bool = True):
    """
    Обновление статуса блокировки сообщений в группе.  Если в группе "False", то блокировка сообщений включена. Если
    "True", то блокировка сообщений выключена.
    """
    try:
        group = Group.get(Group.chat_title == chat_title)
        permission_to_write = "False"
        # Обновляем запись в базе
        Group.update(permission_to_write=permission_to_write).where(
            Group.chat_title == chat_title).execute()
        return {"success": True, "permission_to_write": permission_to_write}
    except Group.DoesNotExist:
        return {"success": False, "error": "Группа не найдена"}
    except Exception as e:
        logger.exception(e)


@app.get("/chat/readonly")
async def chat_readonly(chat_id: int):
    """
   Переводит чат в режим «только чтение». Передаваемый chat_id, должен быть в формате -1001234567890, и являться числовым значением.

   :param chat_id: ID чата, в формате -1001234567890
   :return: Словарь с ключами "success" и "message" или "error"
   """
    try:
        chat_id = str(f"-100{chat_id}")
        await bot.set_chat_permissions(chat_id=int(chat_id), permissions=READ_ONLY)
        return {"success": True, "message": "Чат переведён в режим «только чтение»"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/writeable")
async def chat_writeable(chat_id: int):
    """
    Переводит чат в режим «все могут писать». Передаваемый chat_id, должен быть в формате -1001234567890, и являться
    числовым значением.

    :param chat_id: ID чата, в формате -1001234567890
    """
    try:
        chat_id = str(f"-100{chat_id}")
        await bot.set_chat_permissions(chat_id=chat_id, permissions=FULL_ACCESS)
        return {"success": True, "message": "Чат переведён в режим «все могут писать»"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/set-bad-words")
async def write_bad_words(bad_word: str):
    """
    Записываем плохое слово в базу данных
    """
    try:
        # Получаем информацию о целевой группе (ту, которую хотим ограничить)
        bad_words = BadWords(
            bad_word=bad_word.strip().lower(),  # Получаем слово от пользователя
        )
        bad_words.save()
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/give-privileges")
async def chat_give_privilege(chat_title: str, user_id: int):
    """
    Запись в базу данных пользователей, которым разрешено писать в чате без ограничений

    :param chat_title: название чата
    :param user_id: id пользователя
    """
    try:
        logger.info(f"Выдача привилегий для пользователя {user_id} в чате '{chat_title}'")
        # Получаем информацию о целевой группе (ту, которую хотим ограничить)
        group = Group.get(Group.chat_title == chat_title)
        group_id = group.chat_id

        existing = PrivilegedUsers.select().where(
            (PrivilegedUsers.chat_id == group_id) &
            (PrivilegedUsers.user_id == user_id)
        ).first()

        if not existing:
            privileges = PrivilegedUsers(chat_id=group_id, user_id=user_id, chat_title=chat_title)
            privileges.save()

        return {
            "success": True,
            "message": f"Пользователь {user_id} теперь имеет привилегии в чате '{chat_title}'"
        }

    except Exception as e:
        logger.exception(f"Ошибка при выдаче привилегий: {e}")
        return {"success": False, "error": "Внутренняя ошибка сервера"}


@app.get("/get-chat-id")
async def get_chat_id(title: str):
    """
    Получение названия группы
    """
    group = Group.get(Group.chat_title == title)
    return {"success": True, "chat_id": group.chat_id}


@app.get("/require-subscription")
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
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8080, reload=True)
