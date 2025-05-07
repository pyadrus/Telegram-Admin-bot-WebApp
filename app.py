import uvicorn
from fastapi import FastAPI, Request
from fastapi import Form
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from utils.get_id import get_participants_count
from utils.models import Group, db

app = FastAPI()

# Указываем директорию с шаблонами
templates = Jinja2Templates(directory="templates")
# Подключение статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")


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
        # Создаем таблицу, если она не создана ранее
        db.create_tables([Group], safe=True)
        with db.atomic():
            # Вставляем новую
            Group.insert(chat_id=chat_id, chat_title=chat_title, chat_total=chat_total, chat_link=chat_link).execute()

        return RedirectResponse(url="/formation-groups?success=1", status_code=303)
    except Exception as e:
        return RedirectResponse(url="/formation-groups?error=1", status_code=303)


# Получение списка групп для отображения на странице
@app.get("/api/chat_title")
async def get_groups():
    chat_title = list(Group.select().dicts())
    return {"chat_title": chat_title}


@app.get("/api/get-participants")
async def get_participants(chat_title: str):
    try:
        group = Group.get(Group.chat_title == chat_title)
        # Здесь можно вызвать Telegram API для актуального числа участников
        return {"success": True, "participants_count": group.chat_total}
    except Group.DoesNotExist:
        return {"success": False, "error": "Группа не найдена"}


@app.get("/api/update-participants")
async def update_participants(chat_title: str):
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


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8080, reload=True)
