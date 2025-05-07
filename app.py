import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Form
from models import Group

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
async def save_group(chat_id: str = Form(...)):
    try:
        Group.create(chat_id=chat_id)
        return RedirectResponse(url="/formation-groups?success=1", status_code=303)
    except Exception as e:
        return RedirectResponse(url="/formation-groups?error=1", status_code=303)


# Получение списка групп для отображения на странице
@app.get("/api/groups")
async def get_groups():
    groups = list(Group.select().dicts())
    return {"groups": groups}


@app.get("/api/get-participants")
async def get_participants(chat_id: str):
    # Здесь должен быть реальный запрос к Telegram API
    # Пока просто заглушка:
    return {"success": True, "participants_count": 12345}


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8080, reload=True)
