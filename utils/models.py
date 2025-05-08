from peewee import SqliteDatabase, Model, CharField, IntegerField

# Настройка подключения к базе данных SQLite (или другой базы данных)
db = SqliteDatabase('db/database.db')


class Group(Model):
    """
    Запись групп в базу данных
    (unique=True - для уникальности. Если ссылка уже есть, то запись не будет создана)
    """
    chat_id = IntegerField()  # ID группы
    chat_title = CharField()  # Название группы
    chat_total = IntegerField()  # Общее количество участников
    chat_link = CharField(unique=True)  # Ссылка на группу
    permission_to_write = IntegerField()  # Права на запись в группу

    class Meta:
        database = db  # Указываем, что данная модель будет использовать базу данных
        table_name = "groups_administration"  # Имя таблицы
        primary_key = False  # Для запрета автоматически создающегося поля id (как первичный ключ)


class GroupMembers(Model):
    """Запись в базу данных участников группы, которые подписались или отписались от группы.
    null=True - поле может быть пустым."""
    chat_id = IntegerField()  # Получаем ID чата
    chat_title = CharField()  # Получаем название чата
    user_id = IntegerField()  # Получаем ID пользователя
    username = CharField()  # Получаем username пользователя
    first_name = CharField(null=True)  # Получаем first_name пользователя
    last_name = CharField(null=True)  # Получаем last_name пользователя
    date_now = CharField()  # Получаем текущую дату

    class Meta:
        database = db  # Указываем, что данная модель будет использовать базу данных
        table_name = "group_members_add"  # Имя таблицы
        primary_key = False  # Для запрета автоматически создающегося поля id (как первичный ключ)


def initialize_db():
    db.connect()
    db.create_tables([Group], safe=True)
    db.create_tables([GroupMembers], safe=True)
    db.close()


initialize_db()
