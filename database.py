import os

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv()


def database_url():
    return os.environ["DATABASE_URL"]


def check_database():
    init_db()


def open_database():
    return psycopg.connect(database_url(), row_factory=dict_row)


def close_database(connection):
    connection.close()


def init_db():
    connection = open_database()
    try:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL
            )""")

        count = connection.execute("SELECT COUNT(*) AS n FROM tasks").fetchone()["n"]

        if count == 0:
            with connection.cursor() as cursor:
                cursor.executemany(
                    "INSERT INTO tasks (title, done) VALUES (%s, %s)",
                    [
                        ("Buy groceries", False),
                        ("Read FastAPI docs", True),
                        ("Learn FastAPI", False),
                    ]
                )

        connection.commit()
    finally:
        close_database(connection)


def create_task(title: str, done: bool):
    connection = open_database()
    try:
        row = connection.execute(
            "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING *", (title, done)
        ).fetchone()
        connection.commit()
        return row
    finally:
        close_database(connection)


def update_task(id: int, title: str, done: bool):
    connection = open_database()
    try:
        connection.execute(
            "UPDATE tasks SET title = %s, done = %s WHERE id = %s", (title, done, id)
        )
        connection.commit()
        return {
            "id": id,
            "title": title,
            "done": done
        }
    finally:
        close_database(connection)


def delete_task(id: int):
    connection = open_database()
    try:
        connection.execute("DELETE FROM tasks WHERE id = %s", (id,))
        connection.commit()
    finally:
        close_database(connection)


def select_task():
    connection = open_database()
    try:
        return connection.execute("SELECT * FROM tasks ORDER BY id").fetchall()
    finally:
        close_database(connection)


def where_task(tasks_id):
    connection = open_database()
    try:
        return connection.execute(
            "SELECT * FROM tasks WHERE id = %s", (tasks_id,)
        ).fetchone()
    finally:
        close_database(connection)


if __name__ == "__main__":
    init_db()
    print("Database initialized")
