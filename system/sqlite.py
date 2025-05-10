import sqlite3
from datetime import datetime

from peewee import SqliteDatabase, Model, CharField, IntegerField

# Настройка подключения к базе данных SQLite (или другой базы данных)
db = SqliteDatabase('setting/database.db')
path_database = 'setting/database.db'


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


def get_groups_by_channel_id(update):
    # Выполняем запрос: выбираем все group_id, где required_channel_id совпадает с update.chat.id
    query = GroupRestrictions.select(GroupRestrictions.group_id).where(
        GroupRestrictions.required_channel_id == update.chat.id)

    # Извлекаем результаты как список значений group_id
    groups = [row.group_id for row in query]

    return groups


def get_required_channel_username_for_group(message):
    try:
        # Получаем запись по group_id (message.chat.id)
        restriction = GroupRestrictions.get(GroupRestrictions.group_id == message.chat.id)
        return (restriction.required_channel_username,)
    except GroupRestrictions.DoesNotExist:
        return None


def get_required_channel_for_group(message):
    try:
        # Получаем запись по group_id (message.chat.id)
        restriction = GroupRestrictions.get(GroupRestrictions.group_id == message.chat.id)
        return (restriction.required_channel_id, restriction.required_channel_username)
    except GroupRestrictions.DoesNotExist:
        return None


def set_group_restriction(message, channel_id, channel_username):
    # Создаем или заменяем запись в таблице
    GroupRestrictions.insert(
        group_id=message.chat.id,
        required_channel_id=channel_id,
        required_channel_username=channel_username
    ).on_conflict_replace().execute()


def fetch_user_data():
    with sqlite3.connect(path_database) as conn:
        # Инициализация соединения с базой данных SQLite
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id, user_id FROM privileged_users")
        rows = cursor.fetchall()
        data_dict = {(row[0], row[1]): True for row in rows}
        cursor.close()
        return data_dict


def writing_bad_words_to_the_database(bad_word, user_id, username, user_full_name, chat_id, chat_title):
    """
    Запись запрещенных слов в базу данных setting/bad_words.db, при добавлении нового слова функция ищет дубликаты слов,
    и при нахождении оставляет одно слово без повтора
    """
    # Инициализируем базу данных sqlite
    with sqlite3.connect(path_database) as conn:
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS bad_words (id INTEGER PRIMARY KEY AUTOINCREMENT, word TEXT, '
                       'user_id INTEGER, username TEXT, user_full_name TEXT, chat_id INTEGER, chat_title TEXT)')
        # Получаем список всех слов в базе данных sqlite
        cursor.execute('SELECT word FROM bad_words')
        existing_words = [row[0] for row in cursor.fetchall()]
        # Проверяем, есть ли новое слово уже в списке существующих слов
        if bad_word in existing_words:
            # Если новое слово уже есть в базе данных, то удаляем его
            cursor.execute('DELETE FROM bad_words WHERE word = ?', (bad_word,))
        # Добавляем слово в базу данных sqlite
        cursor.execute('INSERT INTO bad_words (word, user_id, username, user_full_name, chat_id, chat_title) '
                       'VALUES (?, ?, ?, ?, ?, ?)',
                       (bad_word, user_id, username, user_full_name, chat_id, chat_title))
        conn.commit()


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


def reading_from_the_database_of_forbidden_words():
    """
    Чтение с базы данных запрещенных слов
    """
    # Инициализируем базу данных sqlite
    with sqlite3.connect(path_database) as conn:
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS bad_words (id INTEGER PRIMARY KEY AUTOINCREMENT, word TEXT)')
        conn.commit()
        bad_words = cursor.execute('SELECT word FROM bad_words').fetchall()
    return bad_words
