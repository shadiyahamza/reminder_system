import sqlite3
import pandas as pd
import os

# Database path (adjust based on your folder structure)
#DB_PATH = os.path.join("..", "database", "reminders.db")
DB_PATH = r"C:\Users\shadiya\Downloads\automated_reminders\automated_reminders\database\reminders.db"


# 🔹 Connect to Database
def connect_db():
    return sqlite3.connect(DB_PATH)


# 🔹 Create Tables (if not exist)
def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        discord_id TEXT,
        course TEXT NOT NULL
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
    print("✅ Tables verified or created successfully.")


# 🔹 Add New Student
def add_student():
    name = input("Enter student name: ")
    email = input("Enter student email: ")
    discord_id = input("Enter Discord ID: ")
    course = input("Enter course name (e.g., DSA, CyberSecurity, FullStack): ")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO students (name, email, discord_id, course) VALUES (?, ?, ?, ?)",
        (name, email, discord_id, course)
    )
    conn.commit()
    conn.close()
    print(f"✅ Added student: {name} to course {course}")


# 🔹 Add New Class
def add_class():
    course = input("Enter course name (e.g., DSA, CyberSecurity, FullStack): ")
    session_name = input("Enter session name: ")
    date = input("Enter session date (YYYY-MM-DD): ")
    time = input("Enter session time (e.g., 09:00): ")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO classes (course, session_name, date, time) VALUES (?, ?, ?, ?)",
        (course, session_name, date, time)
    )
    conn.commit()
    conn.close()
    print(f"✅ Added class '{session_name}' for {course} on {date} at {time}")


# 🔹 Add New Assignment
def add_assignment():
    course = input("Enter course name (e.g., DSA, CyberSecurity, FullStack): ")
    subject = input("Enter subject name: ")
    due_date = input("Enter due date (YYYY-MM-DD): ")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO assignments (course, subject, due_date) VALUES (?, ?, ?)",
        (course, subject, due_date)
    )
    conn.commit()
    conn.close()
    print(f"📝 Added assignment '{subject}' for {course}, due on {due_date}")


# 🔹 Update Class (Date & Time)
def update_class_time():
    class_id = input("Enter class ID to update: ")
    new_date = input("Enter new date (YYYY-MM-DD): ")
    new_time = input("Enter new time (e.g., 11:00): ")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE classes SET date = ?, time = ? WHERE class_id = ?",
        (new_date, new_time, class_id)
    )
    conn.commit()
    conn.close()
    print(f"⏰ Updated class ID {class_id} → {new_date} at {new_time}")


# 🔹 Update Assignment Due Date
def update_assignment_date():
    assignment_id = input("Enter assignment ID to update: ")
    new_due_date = input("Enter new due date (YYYY-MM-DD): ")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE assignments SET due_date = ? WHERE assignment_id = ?",
        (new_due_date, assignment_id)
    )
    conn.commit()
    conn.close()
    print(f"📅 Updated assignment ID {assignment_id} → new due date {new_due_date}")


# 🔹 Delete Student
def delete_student():
    student_id = input("Enter student ID to delete: ")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
    conn.commit()
    conn.close()
    print(f"🗑️ Deleted student ID {student_id}")


# 🔹 Delete Assignment
def delete_assignment():
    assignment_id = input("Enter assignment ID to delete: ")

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM assignments WHERE assignment_id = ?", (assignment_id,))
    conn.commit()
    conn.close()
    print(f"🗑️ Deleted assignment ID {assignment_id}")


# 🔹 View All Data
def view_all():
    conn = connect_db()
    print("\n=== Students Table ===")
    print(pd.read_sql_query("SELECT * FROM students", conn))

    print("\n=== Classes Table ===")
    print(pd.read_sql_query("SELECT * FROM classes", conn))

    print("\n=== Assignments Table ===")
    print(pd.read_sql_query("SELECT * FROM assignments", conn))
    conn.close()


# 🔹 View Data by Course
def view_by_course():
    course = input("Enter course name to view (e.g., DSA, CyberSecurity, FullStack): ")
    conn = connect_db()

    print(f"\n=== Students Enrolled in {course} ===")
    print(pd.read_sql_query(f"SELECT * FROM students WHERE course = '{course}'", conn))

    print(f"\n=== Class Schedule for {course} ===")
    print(pd.read_sql_query(f"SELECT * FROM classes WHERE course = '{course}'", conn))

    print(f"\n=== Assignments for {course} ===")
    print(pd.read_sql_query(f"SELECT * FROM assignments WHERE course = '{course}'", conn))
    conn.close()


# 🔹 Main Menu
def menu():
    create_tables()

    while True:
        print("\n===== Automated Reminder System - Data Management =====")
        print("1. Add new student")
        print("2. Add new class")
        print("3. Add new assignment")
        print("4. Update class date & time")
        print("5. Update assignment due date")
        print("6. Delete student")
        print("7. Delete assignment")
        print("8. View all data")
        print("9. View data by course")
        print("10. Exit")

        choice = input("\nEnter your choice: ")

        if choice == "1":
            add_student()
        elif choice == "2":
            add_class()
        elif choice == "3":
            add_assignment()
        elif choice == "4":
            update_class_time()
        elif choice == "5":
            update_assignment_date()
        elif choice == "6":
            delete_student()
        elif choice == "7":
            delete_assignment()
        elif choice == "8":
            view_all()
        elif choice == "9":
            view_by_course()
        elif choice == "10":
            print("👋 Exiting... Goodbye!")
            break
        else:
            print("❌ Invalid choice, please try again!")


# 🔹 Run the Program
if __name__ == "__main__":
    menu()
