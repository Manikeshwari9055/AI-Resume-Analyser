
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")


def create_table():
    connection = sqlite3.connect(DB_PATH)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def register_user(username, password):
    connection = sqlite3.connect(DB_PATH)

    try:
        hashed_password = generate_password_hash(password)

        connection.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_password)
        )

        connection.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        connection.close()


def verify_user(username, password):
    connection = sqlite3.connect(DB_PATH)

    user = connection.execute(
        "SELECT password FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    connection.close()

    if user and check_password_hash(user[0], password):
        return True

    return False
