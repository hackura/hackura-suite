import sqlite3
from datetime import datetime
import os

DB_PATH = "payments.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            machine_id TEXT PRIMARY KEY,
            email TEXT,
            plan TEXT DEFAULT 'TRIAL',
            updated_at TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_user(machine_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE machine_id = ?', (machine_id,))
    user = c.fetchone()
    conn.close()
    return user

def update_user_plan(machine_id, email, plan):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now()
    c.execute('''
        INSERT INTO users (machine_id, email, plan, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(machine_id) DO UPDATE SET
            email = excluded.email,
            plan = excluded.plan,
            updated_at = excluded.updated_at
    ''', (machine_id, email, plan, now))
    conn.commit()
    conn.close()

# Initialize on import
if not os.path.exists(DB_PATH):
    init_db()
