import sqlite3

DB_PATH = "database/LFT_DB.db"   # Ensure this is the correct path

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn