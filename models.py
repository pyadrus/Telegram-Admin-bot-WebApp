import os
from peewee import SqliteDatabase, Model, CharField

# Получаем абсолютный путь до текущей директории
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'data', 'groups.db')

# Создаем папку data, если её нет
os.makedirs(os.path.dirname(db_path), exist_ok=True)

db = SqliteDatabase(db_path)


class Group(Model):
    chat_id = CharField(unique=True)  # ID группы

    class Meta:
        database = db


def initialize_db():
    db.connect()
    db.create_tables([Group], safe=True)
    db.close()


initialize_db()
