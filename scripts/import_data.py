import sqlite3
import pandas as pd
import numpy as np
import os

DB_PATH = r"C:\Users\shadiya\Downloads\automated_reminders\automated_reminders\reminders.db"
DATA_DIR = r"C:\Users\shadiya\Downloads\automated_reminders\automated_reminders\data"

#DB_PATH = os.path.join("..", "database", "reminders.db")
#DATA_DIR = os.path.join("..", "data")

def connect_db():
    return sqlite3.connect(DB_PATH)

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        discord_id TEXT,
        course TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS classes (
        class_id INTEGER PRIMARY KEY AUTOINCREMENT,
        course TEXT NOT NULL,
        session_name TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assignments (
        assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        course TEXT NOT NULL,
        subject TEXT NOT NULL,
        due_date TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()


def import_course_data(course_name):
    print(f"📥 Importing data for {course_name}...")

    course_file = os.path.join(DATA_DIR, f"{course_name}.xlsx")
    if not os.path.exists(course_file):
        print(f"❌ File not found for course: {course_name}")
        return

    conn = connect_db()

    classes_df = pd.read_excel(course_file, sheet_name="schedule")
    assignments_df = pd.read_excel(course_file, sheet_name="assignment")

    # Normalize columns
    classes_df.columns = [c.strip().lower() for c in classes_df.columns]
    if "course" not in classes_df.columns:
        classes_df["course"] = course_name

    # Clean date
    classes_df["date"] = pd.to_datetime(classes_df["date"], errors="coerce").dt.strftime("%Y-%m-%d")

    # Clean time
    def parse_time(val):
        if pd.isna(val):
            return None
        val = str(val).strip().split('.')[0]
        for fmt in ("%H:%M", "%H:%M:%S"):
            try:
                return pd.to_datetime(val, format=fmt).strftime("%H:%M")
            except:
                continue
        return "09:00"

    classes_df["time"] = classes_df["time"].apply(parse_time).fillna("09:00")

    # ✅ Drop any class_id column (let DB autogenerate it)
    if "class_id" in classes_df.columns:
        classes_df = classes_df.drop(columns=["class_id"])

    # Insert clean data
    classes_df.to_sql("classes", conn, if_exists="append", index=False)

    # Assignments
    if not assignments_df.empty:
        assignments_df.columns = [c.strip().lower() for c in assignments_df.columns]
        if "course" not in assignments_df.columns:
            assignments_df["course"] = course_name
        assignments_df["due_date"] = pd.to_datetime(assignments_df["due_date"], errors="coerce").dt.strftime("%Y-%m-%d")
        if "assignment_id" in assignments_df.columns:
            assignments_df = assignments_df.drop(columns=["assignment_id"])
        assignments_df.to_sql("assignments", conn, if_exists="append", index=False)

    conn.close()
    print(f"✅ Successfully imported {course_name}")


def import_students():
    # ✅ Fix: Directly look inside DATA_DIR, not "data/data"
    student_file = os.path.join(DATA_DIR, "students.xlsx")
    print("📥 Importing student data...")

    # ✅ Check if file exists
    if not os.path.exists(student_file):
        print(f"❌ Students file not found at: {student_file}")
        return

    # ✅ Connect to database
    conn = connect_db()
    cursor = conn.cursor()

    # Optional: Clear old data before reimport (uncomment if needed)
    # cursor.execute("DELETE FROM students")
    # conn.commit()

    # ✅ Read Excel file
    students_df = pd.read_excel(student_file)

    # ✅ Ensure required columns exist
    required_cols = {"name", "email", "course"}
    if not required_cols.issubset(students_df.columns):
        print("❌ Missing required columns in students.xlsx! Expected columns: name, email, course")
        conn.close()
        return

    # ✅ Remove duplicate emails
    students_df = students_df.drop_duplicates(subset=["email"], keep="first")

    # ✅ Reset index and auto-generate IDs
    students_df.reset_index(drop=True, inplace=True)
    students_df["student_id"] = ["S" + str(i+1).zfill(3) for i in range(len(students_df))]

    # ✅ Insert data safely
    students_df.to_sql("students", conn, if_exists="replace", index=False)

    conn.close()
    print("✅ Student data imported successfully!")




def import_all_courses():
    create_tables()
    courses = ["DSA", "CyberSecurity", "FullStack"]

    import_students()
    for course in courses:
        import_course_data(course)

    print("\n🎓 All course data successfully imported into database!")


if __name__ == "__main__":
    import_all_courses()

