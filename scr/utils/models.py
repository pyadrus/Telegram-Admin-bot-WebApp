from peewee import SqliteDatabase, Model, CharField, IntegerField

# Настройка подключения к базе данных SQLite (или другой базы данных)
db = SqliteDatabase('scr/db/database.db')


def get_privileged_users():
    """
    Получает список привилегированных пользователей (chat_id, user_id)
    """
    try:
        query = PrivilegedUsers.select(
            PrivilegedUsers.chat_id, PrivilegedUsers.user_id)
        return {(row.chat_id, row.user_id) for row in query}
    except Exception as e:
        print(f"Ошибка при получении привилегированных пользователей: {e}")
        return set()


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
        table_name = 'privileged_users'  # Имя таблицы
        primary_key = False  # Для запрета автоматически создающегося поля id (как первичный ключ)


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
    chat_link = CharField(unique=True)  # Ссылка на группу
    permission_to_write = IntegerField()  # Права на запись в группу

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
    db.close()


initialize_db()
