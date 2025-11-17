import sqlite3
import os
from config import Config

DB_PATH = Config.DB_PATH

# Ensure DB folder exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def get_conn():
    """Return DB connection"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """Create users + results tables"""
    conn = get_conn()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
    """)

    # Results table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            report_path TEXT,
            json_report TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
    """)

    conn.commit()
    conn.close()

# If run directly, create tables
if __name__ == "__main__":
    create_tables()
    print(f"Database created at {DB_PATH}")
