import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "reminders.db")

# Ensure data folder exists
os.makedirs(DATA_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create courses table
cursor.execute("""
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_name TEXT,
    mode TEXT,
    batch TEXT
)
""")

# Create students table
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    discord_id TEXT,
    course_id INTEGER,
    FOREIGN KEY(course_id) REFERENCES courses(id)
)
""")

# Create reminder_status table
cursor.execute("""
CREATE TABLE IF NOT EXISTS reminder_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    reminder_type TEXT,
    reminder_time TEXT,
    status TEXT,
    sent_date TEXT,
    FOREIGN KEY(student_id) REFERENCES students(id)
)
""")

conn.commit()
conn.close()
print("✅ Database and tables created successfully!")
