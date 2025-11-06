import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "reminders.db")

os.makedirs(DATA_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ===== CREATE TABLES =====
cursor.execute("""
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_name TEXT,
    mode TEXT,
    batch TEXT
)
""")

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

# ===== INSERT COURSES =====
cursor.execute("DELETE FROM courses")  # remove old courses

courses = [
    ('CyberSecurity_B2_2025_Online', 'Online', 'B2_2025'),
    ('CyberSecurity_B3_2025_Online', 'Online', 'B3_2025'),
    ('DSA_B1_2025_Online', 'Online', 'B1_2025'),
    ('DSA_B3_2025_Offline', 'Offline', 'B3_2025'),
    ('FullStack_B2_2025_Offline', 'Offline', 'B2_2025'),
    ('FullStack_B5_2025_Online', 'Online', 'B5_2025')
]

cursor.executemany("INSERT INTO courses (course_name, mode, batch) VALUES (?, ?, ?)", courses)

conn.commit()
conn.close()

print("✅ Database ready and 6 courses added successfully!")
