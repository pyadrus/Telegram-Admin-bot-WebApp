import sqlite3
from datetime import datetime

path_database = 'setting/database.db'


def writing_to_the_database_about_a_new_user(name_table, chat_id, chat_title, user_id, username, first_name, last_name,
                                             date_now):
    """Запись данных о новом пользователе

    :param name_table: название таблицы
    :param chat_id: id чата
    :param chat_title: название чата
    :param user_id: id пользователя
    :param username: username пользователя
    :param first_name: имя пользователя
    :param last_name: фамилия пользователя
    :param date_now: дата и время
    :return: None
    """
    # Записываем данные в базу данных
    conn = sqlite3.connect(path_database)
    cursor = conn.cursor()
    cursor.execute(
        f"CREATE TABLE IF NOT EXISTS {name_table} (chat_id, chat_title, user_id, username, first_name, last_name, "
        "date_joined)"
    )
    cursor.execute(
        f"INSERT INTO {name_table} (chat_id, chat_title, user_id, username, first_name, last_name, date_joined) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (chat_id, chat_title, user_id, username, first_name, last_name, date_now)
    )
    conn.commit()
    conn.close()


def record_the_id_of_allowed_users(chat_id, user_id, username, first_name, last_name, date_add, admin_id, chat_title):
    """
    Мы записываем идентификатор пользователя, которому будет разрешено выполнение определенных действий в чате,
    в базу данных. Будут сохранены идентификаторы чата и участника чата:

    Аргументы:
    :param chat_id: Идентификатор чата, в котором пользователю будут предоставлены права;
    :param user_id: Идентификатор пользователя, которому будут предоставлены определенные права;
    :param username: username пользователя
    :param first_name: имя пользователя
    :param last_name: фамилия пользователя
    :param date_add: дата добавления идентификатора пользователя в базу данных;
    :param admin_id: идентификатор администратора, который добавил пользователя в базу данных;
    :param chat_title: название чата
    :return: None
    """
    with sqlite3.connect(path_database) as conn:
        # Инициализация соединения с базой данных SQLite
        cursor = conn.cursor()
        # Создание таблицы пользователей, если ее еще нет
        cursor.execute("""CREATE TABLE IF NOT EXISTS privileged_users 
                       (chat_id, user_id,username, first_name,last_name, date_add, admin_id, chat_title)""")
        # Записываем ID пользователя в базу данных
        cursor.execute("INSERT INTO privileged_users "
                       "(chat_id, user_id, username, first_name, last_name, date_add, admin_id, chat_title) "
                       "VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (chat_id, user_id, username, first_name,
                                                           last_name, date_add, admin_id, chat_title))
        conn.commit()


def reading_data_from_the_database():
    conn = sqlite3.connect(path_database)
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id, user_id FROM privileged_users")
    rows = cursor.fetchall()
    data_dict = {(row[0], row[1]): True for row in rows}
    cursor.close()
    conn.close()
    return data_dict


def writing_bad_words_to_the_database(bad_word, user_id, username, user_full_name, chat_id, chat_title):
    """
    Запись запрещенных слов в базу данных setting/bad_words.db, при добавлении нового слова функция ищет дубликаты слов,
    и при нахождении оставляет одно слово без повтора"""
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


def writing_check_words_to_the_database(bad_word, user_id, username, user_full_name, chat_id, chat_title):
    """
    Запись check слов в базу данных setting/bad_words.db, при добавлении нового слова функция ищет дубликаты слов, и при
    нахождении оставляет одно слово без повтора"""
    # Инициализируем базу данных sqlite
    with sqlite3.connect(path_database) as conn:
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS check_words (id INTEGER PRIMARY KEY AUTOINCREMENT, word TEXT, '
                       'user_id INTEGER, username TEXT, user_full_name TEXT, chat_id INTEGER, chat_title TEXT)')
        # Получаем список всех слов в базе данных sqlite
        cursor.execute('SELECT word FROM bad_words')
        existing_words = [row[0] for row in cursor.fetchall()]
        # Проверяем, есть ли новое слово уже в списке существующих слов
        if bad_word in existing_words:
            # Если новое слово уже есть в базе данных, то удаляем его
            cursor.execute('DELETE FROM check_words WHERE word = ?', (bad_word,))
        # Добавляем слово в базу данных sqlite
        cursor.execute('INSERT INTO check_words (word, user_id, username, user_full_name, chat_id, chat_title) '
                       'VALUES (?, ?, ?, ?, ?, ?)',
                       (bad_word, user_id, username, user_full_name, chat_id, chat_title))
        conn.commit()


async def delete_bad_word(word):
    """Удаление плохих слов с базы данных"""
    # создаем подключение к базе данных
    with sqlite3.connect(path_database) as conn:
        cursor = conn.cursor()
        # удаляем слово из таблицы
        cursor.execute('DELETE FROM bad_words WHERE word = ?', (word,))
        conn.commit()


def recording_actions_in_the_database(word, message):
    """Запись действий в базу данных запрещенных слов"""
    # Создаем соединение с базой данных
    conn = sqlite3.connect(path_database)
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
    conn.execute("INSERT INTO bad_word_users (user_id, username, full_name, word, timestamp) VALUES (?, ?, ?, ?, ?)",
                 (user_id, username, full_name, word, datetime.now()))
    conn.commit()
    # Закрываем соединение с базой данных
    conn.close()


def recording_actions_check_word_in_the_database(word, message):
    """Запись действий в базу данных check слов"""
    # Создаем соединение с базой данных
    conn = sqlite3.connect(path_database)
    # Создаем таблицы для хранения информации о пользователях, использующих запрещенные слова, и самих запрещенных слов
    conn.execute('''CREATE TABLE IF NOT EXISTS check_word_users (user_id INTEGER, username TEXT, full_name TEXT,
                                                                 word TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS check_word_users (word TEXT)''')
    # Получаем информацию о пользователе
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    # Записываем информацию о пользователе в базу данных
    conn.execute("INSERT INTO check_word_users (user_id, username, full_name, word, timestamp) VALUES (?, ?, ?, ?, ?)",
                 (user_id, username, full_name, word, datetime.now()))
    conn.commit()
    # Закрываем соединение с базой данных
    conn.close()


def reading_from_the_database_of_forbidden_words():
    """Чтение с базы данных запрещенных слов"""
    # Инициализируем базу данных sqlite
    with sqlite3.connect(path_database) as conn:
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS bad_words (id INTEGER PRIMARY KEY AUTOINCREMENT, word TEXT)')
        conn.commit()
        bad_words = cursor.execute('SELECT word FROM bad_words').fetchall()
    return bad_words


def reading_bad_words_from_the_database():
    """Чтение списка запрещенных слов из базы данных"""
    with sqlite3.connect(path_database) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT word FROM bad_words')
        data = cursor.fetchall()
        # Преобразуем список кортежей в список слов
        words = [row[0] for row in data]
        return words


async def reading_data_from_the_database_check():
    """Чтение с базы данных check слов"""
    # Создаем соединение с базой данных
    conn = sqlite3.connect(path_database)
    # Получаем данные из базы данных
    data = conn.execute("SELECT * FROM check_word_users").fetchall()
    # Закрываем соединение с базой данных
    conn.close()
    return data


async def reading_from_the_database_of_forbidden_check_word():
    """Чтение из базы данных запрещенных слов"""
    # Инициализируем базу данных sqlite
    with sqlite3.connect(path_database) as conn:
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS check_words (id INTEGER PRIMARY KEY AUTOINCREMENT, word TEXT)')
        conn.commit()
        check_words = cursor.execute('SELECT word FROM check_words').fetchall()
    return check_words


if __name__ == '__main__':
    reading_data_from_the_database()
    reading_from_the_database_of_forbidden_check_word()
    reading_data_from_the_database_check()
    reading_bad_words_from_the_database()
    reading_from_the_database_of_forbidden_words()
