import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "attendance.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            face_encoding BLOB NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            date TEXT NOT NULL,
            time_in TEXT,
            time_out TEXT,
            UNIQUE(student_id, date)
        )
    """)
    conn.commit()
    conn.close()

def add_student(student_id, full_name, encoding_bytes):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO students (student_id, full_name, face_encoding) VALUES (?, ?, ?)",
        (student_id, full_name, encoding_bytes)
    )
    conn.commit()
    conn.close()

def get_all_students():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT student_id, full_name, face_encoding FROM students")
    rows = cur.fetchall()
    conn.close()
    return rows

def log_attendance(student_id):
    conn = get_connection()
    cur = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now().strftime("%H:%M:%S")

    cur.execute(
        "SELECT time_in, time_out FROM attendance WHERE student_id=? AND date=?",
        (student_id, today)
    )
    row = cur.fetchone()

    if row is None:
        cur.execute(
            "INSERT INTO attendance (student_id, date, time_in) VALUES (?, ?, ?)",
            (student_id, today, now)
        )
        conn.commit()
        conn.close()
        return "time_in", now
    else:
        time_in, time_out = row
        if time_out is None:
            cur.execute(
                "UPDATE attendance SET time_out=? WHERE student_id=? AND date=?",
                (now, student_id, today)
            )
            conn.commit()
            conn.close()
            return "time_out", now
        else:
