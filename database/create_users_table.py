import sqlite3

DB_PATH = "database/LFT_DB.db"

def create_users_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        last_name TEXT,
        email TEXT,
        phone TEXT,
        gender TEXT,
        position TEXT,
        affiliation TEXT
    )
    """)

    conn.commit()
    conn.close()

    print("✅ users table created")


