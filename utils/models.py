from peewee import SqliteDatabase, Model, CharField

# Настройка подключения к базе данных SQLite (или другой базы данных)
db = SqliteDatabase('db/database.db')


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
