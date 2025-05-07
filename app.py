import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Указываем директорию с шаблонами
templates = Jinja2Templates(directory="templates")
# Подключение статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")


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


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8080, reload=True)
