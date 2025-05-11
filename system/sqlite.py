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
