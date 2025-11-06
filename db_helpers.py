# db_helpers.py
import sqlite3
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")
DB_NAME = "reminders.db"

def log_reminder(student_id, reminder_type, status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminder_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            reminder_type TEXT,
            reminder_time TEXT,
            status TEXT,
            sent_date TEXT
        )
    """)
    conn.commit()
    sent_date = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S") if status == "Sent" else None
    cursor.execute("""
        INSERT INTO reminder_status (student_id, reminder_type, reminder_time, status, sent_date)
        VALUES (?, ?, datetime('now'), ?, ?)
    """, (student_id, reminder_type, status, sent_date))
    conn.commit()
    conn.close()
