import configparser

from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage

config = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
# Считываем токен бота с файла config.ini
config.read("setting/config.ini")
bot_token = config.get('BOT_TOKEN', 'BOT_TOKEN')
time_del = config.get('TIME_DEL', 'TIME_DEL')

# Инициализация бота и диспетчера
bot = Bot(token=bot_token)
storage = MemoryStorage()  # Хранилище
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)
