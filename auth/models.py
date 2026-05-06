# auth/models.py
import sqlite3
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB = BASE_DIR / "database" / "users.db"


# =========================
# DATABASE CONNECTION
# =========================
def get_db():
    conn = sqlite3.connect(DB, timeout=10, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout = 5000")
    conn.row_factory = sqlite3.Row
    return conn

# =========================
# INIT TABLE
# =========================
def init_user_table():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        last_name TEXT,
        birthday TEXT,
        email TEXT UNIQUE,
        phone TEXT UNIQUE,
        gender TEXT,
        position TEXT,
        affiliation TEXT,
        password TEXT,
        verified INTEGER DEFAULT 0,
        otp TEXT,
        otp_expiry REAL,
        recovery TEXT,
        agreed INTEGER,
        failed_attempts INTEGER DEFAULT 0,
        lock_until REAL DEFAULT 0,
        created_at REAL,
        password_changed_at REAL,
        role TEXT DEFAULT 'user'
    )
    """)

    conn.commit()
    conn.close()


# =========================
# CREATE USER
# =========================
def create_user(data, hashed_password, otp, expiry):
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM users")
    count = c.fetchone()[0]

    role = "admin" if count == 0 else "user"

    c.execute("""
    INSERT INTO users (
        full_name, last_name, birthday, email, phone, gender,
        position, affiliation, password,
        verified, otp, otp_expiry, recovery, agreed,
        failed_attempts, lock_until, created_at,
        password_changed_at, role
    ) VALUES (
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
    )
    """, (
        data["full_name"],
        data["last_name"],
        data["birthday"],
        data["email"],
        data["phone"],
        data["gender"],
        data["position"],
        data["affiliation"],
        hashed_password,
        0,              # verified default
        otp,
        expiry,
        data["recovery"],
        1,
        0,              # failed_attempts
        0,              # lock_until
        time.time(),
        time.time(),    # password_changed_at
        role
    ))

    conn.commit()
    conn.close()


# =========================
# GET USER
# =========================
def get_user_by_login(value):
    conn = get_db()
    c = conn.cursor()

    c.execute(
        "SELECT * FROM users WHERE email=? OR phone=?",
        (value, value)
    )

    user = c.fetchone()
    conn.close()

    return user


# =========================
# VERIFY USER
# =========================
def verify_user(email):
    conn = get_db()
    c = conn.cursor()

    c.execute(
        "UPDATE users SET verified=1 WHERE email=?",
        (email,)
    )

    conn.commit()
    conn.close()


# =========================
# LOGIN FAIL HANDLING
# =========================
def update_login_fail(user_id, attempts, lock_until=None):
    conn = get_db()
    c = conn.cursor()

    if lock_until:
        c.execute("""
        UPDATE users 
        SET failed_attempts=?, lock_until=? 
        WHERE id=?
        """, (attempts, lock_until, user_id))
    else:
        c.execute("""
        UPDATE users 
        SET failed_attempts=? 
        WHERE id=?
        """, (attempts, user_id))

    conn.commit()
    conn.close()


def reset_fail(user_id):
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    UPDATE users 
    SET failed_attempts=0, lock_until=0 
    WHERE id=?
    """, (user_id,))

    conn.commit()
    conn.close()


# =========================
# PASSWORD RESET (OTP)
# =========================
def set_reset_otp(email, otp, expiry):
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    UPDATE users 
    SET otp=?, otp_expiry=? 
    WHERE email=?
    """, (otp, expiry, email))

    conn.commit()
    conn.close()


def update_password(email, hashed_password):
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    UPDATE users 
    SET password=?, password_changed_at=? 
    WHERE email=?
    """, (hashed_password, time.time(), email))

    conn.commit()
    conn.close()


# =========================
# ADMIN
# =========================
def get_all_users():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    SELECT id, full_name, email, phone, role, verified, recovery
    FROM users
    """)

    rows = c.fetchall()
    conn.close()

    # CONVERT TO DICTIONARY LIST
    users = []
    for row in rows:
        users.append({
            "id": row["id"],
            "full_name": row["full_name"],
            "email": row["email"],
            "phone": row["phone"],
            "role": row["role"],
            "verified": row["verified"],
            "recovery": row["recovery"]
        })

    return users