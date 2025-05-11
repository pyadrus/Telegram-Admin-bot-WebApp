import sqlite3
from datetime import datetime

from utils.models import path_database


def fetch_user_data():
    with sqlite3.connect(path_database) as conn:
        # Инициализация соединения с базой данных SQLite
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id, user_id FROM privileged_users")
        rows = cursor.fetchall()
        data_dict = {(row[0], row[1]): True for row in rows}
        cursor.close()
        return data_dict



def recording_actions_in_the_database(word, message):
    """
    Запись действий в базу данных запрещенных слов
    """
    # Создаем соединение с базой данных
    with sqlite3.connect(path_database) as conn:
        # Инициализация соединения с базой данных SQLite
        # Создаем таблицы для хранения информации о пользователях, использующих запрещенные слова, и самих запрещенных слов
        conn.execute('''CREATE TABLE IF NOT EXISTS bad_word_users
                         (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, username TEXT, full_name TEXT,
                          word TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS bad_words (id INTEGER PRIMARY KEY AUTOINCREMENT, word TEXT)''')
        # Проверяем, является ли слово запрещенным
        conn.execute("SELECT id FROM bad_words WHERE word=?", (word,)).fetchone()
        # Получаем информацию о пользователе
        user_id = message.from_user.id
        username = message.from_user.username
        full_name = message.from_user.full_name
        conn.execute(
            "INSERT INTO bad_word_users (user_id, username, full_name, word, timestamp) VALUES (?, ?, ?, ?, ?)",
            (user_id, username, full_name, word, datetime.now()))
        conn.commit()



