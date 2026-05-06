import sqlite3

DB_PATH = "database/LFT_DB.db"

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()

    return [dict(u) for u in users]