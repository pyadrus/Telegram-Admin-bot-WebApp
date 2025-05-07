import os
from peewee import SqliteDatabase, Model, CharField

# Получаем абсолютный путь до текущей директории
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'data', 'groups.db')

os.makedirs(os.path.dirname(db_path), exist_ok=True)  # Создаем папку data, если её нет

db = SqliteDatabase(db_path)


class Group(Model):
    """Запись групп в базу данных"""
    chat_id = CharField()  # ID группы
    chat_title = CharField()  # Название группы
    chat_total = CharField()  # Общее количество участников
    chat_link = CharField()  # Ссылка на группу

    class Meta:
        database = db  # Указываем, что данная модель будет использовать базу данных
        table_name = "groups_administration"  # Имя таблицы
        primary_key = False  # Для запрета автоматически создающегося поля id (как первичный ключ)


def initialize_db():
    db.connect()
    db.create_tables([Group], safe=True)
    db.close()


initialize_db()
