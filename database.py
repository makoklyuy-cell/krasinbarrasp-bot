import sqlite3
from datetime import datetime
from config import DATABASE_PATH

def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            username TEXT UNIQUE,
            name TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            bartender TEXT NOT NULL,
            is_reserve BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(date, time, bartender)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS swap_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user TEXT NOT NULL,
            to_user TEXT NOT NULL,
            shift_date TEXT NOT NULL,
            shift_time TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ База данных инициализирована")

def add_user(telegram_id, username, name):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT OR REPLACE INTO users (telegram_id, username, name, is_active) VALUES (?, ?, ?, 1)',
            (telegram_id, username, name)
        )
        conn.commit()
    finally:
        conn.close()

def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def add_shift(date, time, bartender, is_reserve=False):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT OR REPLACE INTO shifts (date, time, bartender, is_reserve) VALUES (?, ?, ?, ?)',
            (date, time, bartender, is_reserve)
        )
        conn.commit()
    finally:
        conn.close()

def get_shifts_by_date(date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM shifts WHERE date = ? ORDER BY time', (date,))
    shifts = cursor.fetchall()
    conn.close()
    return shifts

def get_shifts_by_bartender(bartender):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM shifts WHERE bartender = ? ORDER BY date, time', (bartender,))
    shifts = cursor.fetchall()
    conn.close()
    return shifts

def get_all_shifts():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM shifts ORDER BY date, time')
    shifts = cursor.fetchall()
    conn.close()
    return shifts

def delete_all_shifts():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM shifts')
    conn.commit()
    conn.close()

def get_last_generation_date():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM settings WHERE key = "last_generation"')
    row = cursor.fetchone()
    conn.close()
    return row['value'] if row else None

def set_last_generation_date(date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES ("last_generation", ?, CURRENT_TIMESTAMP)',
        (date,)
    )
    conn.commit()
    conn.close()

def create_swap_request(from_user, to_user, shift_date, shift_time):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO swap_requests (from_user, to_user, shift_date, shift_time, status) VALUES (?, ?, ?, ?, ?)',
        (from_user, to_user, shift_date, shift_time, 'pending')
    )
    conn.commit()
    request_id = cursor.lastrowid
    conn.close()
    return request_id

def get_swap_requests_for_user(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM swap_requests WHERE to_user = ? AND status = 'pending' ORDER BY created_at DESC",
        (username,)
    )
    requests = cursor.fetchall()
    conn.close()
    return requests

def approve_swap_request(request_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM swap_requests WHERE id = ?', (request_id,))
    request = cursor.fetchone()
    if request:
        cursor.execute('UPDATE swap_requests SET status = ? WHERE id = ?', ('approved', request_id))
        cursor.execute(
            'UPDATE shifts SET bartender = ? WHERE date = ? AND time = ? AND bartender = ?',
            (request['to_user'], request['shift_date'], request['shift_time'], request['from_user'])
        )
        conn.commit()
    conn.close()
    return request

def reject_swap_request(request_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE swap_requests SET status = ? WHERE id = ?', ('rejected', request_id))
    conn.commit()
    conn.close()

