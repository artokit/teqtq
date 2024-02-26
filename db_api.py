import sqlite3
from sqlite3 import IntegrityError

connect = sqlite3.connect('db.sqlite')
cursor = connect.cursor()


def get_users():
    return cursor.execute('SELECT * FROM USERS').fetchall()


def add_user(user_id):
    try:
        cursor.execute('INSERT INTO USERS VALUES(?)', (user_id,))
        connect.commit()
    except IntegrityError:
        pass
