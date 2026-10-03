import sqlite3
import os
import json
from datetime import datetime

DB_PATH = "database/axiomguard.db"


def get_connection():
    os.makedirs("database", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            hashed_password TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            module TEXT NOT NULL,
            target TEXT NOT NULL,
            verdict TEXT,
            score REAL,
            result_json TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Migration safety net: if scan_history already existed from before
    # (without user_id), add the column so old DBs don't break.
    cursor.execute("PRAGMA table_info(scan_history)")
    existing_cols = [row[1] for row in cursor.fetchall()]
    if "user_id" not in existing_cols:
        cursor.execute("ALTER TABLE scan_history ADD COLUMN user_id INTEGER")

    conn.commit()
    conn.close()
    print("✅ Database initialized")


# ── User account functions ──────────────────────────────────────

def create_user(name: str, email: str, hashed_password: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (name, email, hashed_password, created_at)
        VALUES (?, ?, ?, ?)
    ''', (name, email, hashed_password, datetime.now().isoformat()))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id


def get_user_by_email(email: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email, created_at FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def save_scan(module: str, target: str, verdict: str, score: float, result: dict, user_id: int = None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO scan_history (user_id, module, target, verdict, score, result_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, module, target, verdict, score, json.dumps(result), datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_history(limit: int = 20, user_id: int = None):
    conn = get_connection()
    cursor = conn.cursor()
    if user_id is not None:
        cursor.execute('''
            SELECT id, module, target, verdict, score, created_at
            FROM scan_history
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (user_id, limit))
    else:
        cursor.execute('''
            SELECT id, module, target, verdict, score, created_at
            FROM scan_history
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_history_detail(entry_id: int, user_id: int = None):
    conn = get_connection()
    cursor = conn.cursor()
    if user_id is not None:
        cursor.execute('SELECT * FROM scan_history WHERE id = ? AND user_id = ?', (entry_id, user_id))
    else:
        cursor.execute('SELECT * FROM scan_history WHERE id = ?', (entry_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        data = dict(row)
        data['result_json'] = json.loads(data['result_json'])
        return data
    return None


def delete_scan(entry_id: int, user_id: int = None):
    conn = get_connection()
    cursor = conn.cursor()
    if user_id is not None:
        cursor.execute('DELETE FROM scan_history WHERE id = ? AND user_id = ?', (entry_id, user_id))
    else:
        cursor.execute('DELETE FROM scan_history WHERE id = ?', (entry_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def clear_history(user_id: int = None):
    conn = get_connection()
    cursor = conn.cursor()
    if user_id is not None:
        cursor.execute('DELETE FROM scan_history WHERE user_id = ?', (user_id,))
    else:
        cursor.execute('DELETE FROM scan_history')
    conn.commit()
    conn.close()