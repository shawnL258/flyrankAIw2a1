import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "tasks.db"

def check_database():
    init_db()

def open_database():
    connection = sqlite3.connect(DB_PATH)
    return connection

def close_database(connection):
    connection.close()

def mapped_records_to_json(connection):
    connection.row_factory = sqlite3.Row
    
def init_db():
    connection = open_database()
    try:
        cursor = connection.cursor()
        cursor.execute(
                """CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    done BOOLEAN NOT NULL
                )""")
        
        count = connection.execute(
            "SELECT COUNT(*) FROM tasks"
        ).fetchone()[0]
        
        if count == 0:
            connection.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
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
        cursor = connection.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)", (title, done)
        )
        connection.commit()
        return {
            "id" : cursor.lastrowid,
            "title" : title,
            "done" : done
        }
    finally:
        close_database(connection)

def update_task(id: int, title: str, done: bool):
    connection = open_database()
    try:
        cursor = connection.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?", (title, done, id)
        )
        connection.commit()
        return {
            "id" : id,
            "title" : title,
            "done" : done
        }
    finally:
        close_database(connection)

def delete_task(id: int):
    connection = open_database()
    try:
        cursor = connection.execute(
            "DELETE FROM tasks WHERE id = ?", (id,)
        )
        connection.commit()
    finally:
        close_database(connection)

def select_task():
    connection = open_database()
    mapped_records_to_json(connection)
    try:
        rows = connection.execute("SELECT * FROM tasks").fetchall()
        return [{**dict(row), "done": bool(row["done"])} for row in rows]
    finally:
        close_database(connection)

def where_task(tasks_id):
    connection = open_database()
    mapped_records_to_json(connection)

    try:
        row = connection.execute("SELECT * FROM tasks WHERE id = ?", (tasks_id,)).fetchone()
        return {**dict(row), "done": bool(row["done"])} if row is not None else None
    finally:
        close_database(connection)


if __name__ == "__main__":
    init_db()
    print("Database initialized")
