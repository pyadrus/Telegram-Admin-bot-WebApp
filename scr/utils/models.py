# -*- coding: utf-8 -*-
from peewee import SqliteDatabase, Model, CharField, IntegerField

# Настройка подключения к базе данных SQLite (или другой базы данных)
db = SqliteDatabase(f"scr/db/database.db")


def get_privileged_users():
    """
    Получает список привилегированных пользователей (chat_id, user_id)
    """
    try:
        query = PrivilegedUsers.select(PrivilegedUsers.chat_id, PrivilegedUsers.user_id)
        return {(row.chat_id, row.user_id) for row in query}
    except Exception as e:
        print(f"Ошибка при получении привилегированных пользователей: {e}")
        return set()


class Groups(Model):
    """
    Модель для хранения групп / каналов для отслеживания.
    """

    username_chat_channel = CharField(unique=True)  # Получаем username группы

    class Meta:
        database = db  # Указываем, что данная модель будет использовать базу данных
        table_name = "groups"  # Имя таблицы
        primary_key = (
            False  # Для запрета автоматически создающегося поля id (как первичный ключ)
        )


class BadWords(Model):
    """
    Модель для хранения запрещенных слов.

    :cvar bad_word: Поле для хранения запрещенного слова.
    """

    bad_word = CharField()  # Получаем ID

    class Meta:
        """
        Метакласс для настройки модели.

        :cvar database: База данных, используемая моделью.
        :cvar table_name: Имя таблицы в базе данных.
        """

        database = db  # Указываем, что данная модель будет использовать базу данных
        table_name = "bad_words"  # Имя таблицы


class PrivilegedUsers(Model):
    chat_id = IntegerField()  # Получаем ID
    user_id = IntegerField()  # Получаем ID пользователя
    chat_title = CharField()  # Получаем название группы

    class Meta:
        database = db  # Указываем, что данная модель будет использовать базу данных
        table_name = "privileged_users"  # Имя таблицы
        primary_key = (
            False  # Для запрета автоматически создающегося поля id (как первичный ключ)
        )


class GroupRestrictions(Model):
    """
    Записывает в базу данных идентификатор чата, для проверки подписки.
    """

    group_id = IntegerField()  # Получаем ID чата
    required_channel_id = IntegerField()  # Получаем ID чата
    required_channel_username = CharField()  # Получаем username чата

    class Meta:
        """
        Метакласс для настройки модели.

        :cvar database: База данных, используемая моделью.
        :cvar table_name: Имя таблицы в базе данных.
        """

        database = db  # Указываем, что данная модель будет использовать базу данных
        table_name = "group_restrictions"  # Имя таблицы
        # Для запрета автоматически создающегося поля id (как первичный ключ)
        primary_key = False


class Group(Model):
    """
    Запись групп в базу данных
    (unique=True - для уникальности. Если ссылка уже есть, то запись не будет создана)
    """
    chat_id = IntegerField()  # ID группы
    chat_title = CharField()  # Название группы
    chat_total = IntegerField()  # Общее количество участников
    chat_link = CharField()  # Ссылка на группу
    permission_to_write = IntegerField()  # Права на запись в группу
    user_id = IntegerField()  # ID пользователя

    class Meta:
        """
        Метакласс для настройки модели.

        :cvar database: База данных, используемая моделью.
        :cvar table_name: Имя таблицы в базе данных.
        """

        database = db  # Указываем, что данная модель будет использовать базу данных
        table_name = "groups_administration"  # Имя таблицы
        # Для запрета автоматически создающегося поля id (как первичный ключ)
        primary_key = False
        # Составной уникальный индекс: (chat_link, user_id)
        indexes = (
            (('chat_link', 'user_id'), True),  # True = UNIQUE
        )


class GroupMembers(Model):
    """
    Запись в базу данных участников группы, которые подписались или отписались от группы.
    (null=True - поле может быть пустым.)
    """

    chat_id = IntegerField()  # Получаем ID чата
    chat_title = CharField()  # Получаем название чата
    user_id = IntegerField()  # Получаем ID пользователя
    username = CharField(null=True)  # Получаем username пользователя
    first_name = CharField(null=True)  # Получаем first_name пользователя
    last_name = CharField(null=True)  # Получаем last_name пользователя
    date_now = CharField()  # Получаем текущую дату

    class Meta:
        """
        Метакласс для настройки модели.

        :cvar database: База данных, используемая моделью.
        :cvar table_name: Имя таблицы в базе данных.
        """

        database = db  # Указываем, что данная модель будет использовать базу данных
        table_name = "group_members_add"  # Имя таблицы
        # Для запрета автоматически создающегося поля id (как первичный ключ)
        primary_key = False


def add_column_if_not_exists(table_name: str, column_name: str, column_type: str):
    """
    Проверяет, существует ли столбец в таблице, и добавляет его, если отсутствует.

    :param table_name: Название таблицы
    :param column_name: Название столбца
    :param column_type: Тип столбца (TEXT, INTEGER, REAL, BLOB)
    """
    # Получаем информацию о столбцах таблицы
    cursor = db.execute_sql(f"PRAGMA table_info({table_name});")
    columns = [row[1] for row in cursor.fetchall()]  # row[1] — это имя столбца

    if column_name not in columns:
        try:
            db.execute_sql(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};")
            print(f"✅ Столбец '{column_name}' добавлен в таблицу '{table_name}'.")
        except Exception as e:
            print(f"❌ Ошибка при добавлении столбца '{column_name}': {e}")
    else:
        print(f"ℹ️ Столбец '{column_name}' уже существует в таблице '{table_name}'.")


def initialize_db():
    """
    Инициализирует базу данных, создавая необходимые таблицы.

    :return: None
    """
    db.connect()

    db.create_tables([Group], safe=True)
    db.create_tables([GroupMembers], safe=True)
    db.create_tables([PrivilegedUsers], safe=True)
    db.create_tables([GroupRestrictions], safe=True)
    db.create_tables([BadWords], safe=True)

    # Добавляем столбец user_id в таблицу groups_administration, если его нет
    # add_column_if_not_exists(
    #     table_name="groups_administration",
    #     column_name="user_id",
    #     column_type="INTEGER"
    # )

    db.close()


initialize_db()
