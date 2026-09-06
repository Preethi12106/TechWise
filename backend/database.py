import sqlite3
from pathlib import Path

DB_NAME = Path(__file__).resolve().parent / "techwise.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_table():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            decision TEXT NOT NULL,
            context TEXT,
            reason TEXT,
            alternatives TEXT,
            consequences TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_table()
    print("Database and table created successfully.")