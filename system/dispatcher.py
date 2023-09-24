from aiogram import Bot, Dispatcher
import configparser

from aiogram.contrib.fsm_storage.memory import MemoryStorage

config = configparser.ConfigParser(empty_lines_in_values=False, allow_no_value=True)
# Считываем токен бота с файла config.ini
config.read("setting/config.ini")
bot_token = config.get('BOT_TOKEN', 'BOT_TOKEN')

# Инициализация бота и диспетчера
bot = Bot(token=bot_token, parse_mode="HTML")
# parse_mode="HTML" - разметка сообщения HTML
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
