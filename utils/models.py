import sqlite3

from peewee import SqliteDatabase, Model, CharField, IntegerField

# Настройка подключения к базе данных SQLite (или другой базы данных)
db = SqliteDatabase('db/database.db')
# Настройка подключения к базе данных SQLite (или другой базы данных)
path_database = 'db/database.db'


def reading_from_the_database_of_forbidden_words():
    """
    Чтение с базы данных запрещенных слов
    """
    # Инициализируем базу данных sqlite
    with sqlite3.connect(path_database) as conn:
        cursor = conn.cursor()
        conn.commit()
        bad_words = cursor.execute('SELECT word FROM bad_words').fetchall()
    return bad_words

class BadWords(Model):
    bad_word = CharField()  # Получаем ID

    class Meta:
        database = db  # Указываем, что данная модель будет использовать базу данных
        table_name = "bad_words"  # Имя таблицы
        primary_key = False  # Для запрета автоматически создающегося поля id (как первичный ключ)


class GroupRestrictions(Model):
    """
    Записывает в базу данных идентификатор чата, для проверки подписки.
    """

    group_id = IntegerField()  # Получаем ID чата
    required_channel_id = IntegerField()  # Получаем ID чата
    required_channel_username = CharField()  # Получаем username чата

    class Meta:
        database = db  # Указываем, что данная модель будет использовать базу данных
        table_name = "group_restrictions"  # Имя таблицы
        primary_key = False  # Для запрета автоматически создающегося поля id (как первичный ключ)


class PrivilegedUsers(Model):
    """
    Записывает в базу данных идентификатор пользователя, которому будет разрешено выполнение определенных действий в чате,
    в базу данных. Будут сохранены идентификаторы чата и участника чата:
    """

    chat_id = IntegerField()  # Получаем ID чата
    user_id = IntegerField()  # Получаем ID пользователя
    username = CharField()  # Получаем username пользователя
    first_name = CharField(null=True)  # Получаем first_name пользователя
    last_name = CharField(null=True)  # Получаем last_name пользователя
    date_add = CharField()  # Получаем текущую дату
    admin_id = IntegerField()  # Получаем ID администратора, который добавил пользователя в базу данных
    chat_title = CharField()  # Получаем название чата

    class Meta:
        database = db  # Указываем, что данная модель будет использовать базу данных
        table_name = "privileged_users"  # Имя таблицы
        primary_key = False  # Для запрета автоматически создающегося поля id (как первичный ключ)


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
    """
    Запись в базу данных участников группы, которые подписались или отписались от группы.
    (null=True - поле может быть пустым.)
    """
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
    db.create_tables([PrivilegedUsers], safe=True)
    db.create_tables([GroupRestrictions], safe=True)
    db.create_tables([BadWords], safe=True)
    db.close()


initialize_db()
