
import os
import psycopg2
from psycopg2 import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash


def get_connection():
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is missing")

    return psycopg2.connect(database_url)


def create_table():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(100) NOT NULL UNIQUE,
                    password TEXT NOT NULL
                )
            """)
        connection.commit()

    finally:
        connection.close()


def register_user(username, password):
    connection = get_connection()

    try:
        hashed_password = generate_password_hash(password)

        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, hashed_password)
            )

        connection.commit()
        return True

    except IntegrityError:
        connection.rollback()
        return False

    finally:
        connection.close()


def verify_user(username, password):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT password FROM users WHERE username = %s",
                (username,)
            )
            user = cursor.fetchone()

        if user and check_password_hash(user[0], password):
            return True

        return False

    finally:
        connection.close()
