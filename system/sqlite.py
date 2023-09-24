import sqlite3

path_database = 'setting/database.db'


def writing_to_the_database_about_a_new_user(name_table, chat_id, chat_title, user_id, username, first_name, last_name,
                                             date_now):
    """Запись данных о новом пользователе"""
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
    chat_id - идентификатор чата, в котором пользователю будут предоставлены права;
    user_id - идентификатор пользователя, которому будут предоставлены определенные права;
    username - username пользователя
    first_name - имя пользователя
    last_name - фамилия пользователя
    date_add - дата добавления идентификатора пользователя в базу данных;
    admin_id - идентификатор администратора, который добавил пользователя в базу данных;
    chat_title - название чата
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


if __name__ == '__main__':
    reading_data_from_the_database()
