import sqlite3
from datetime import datetime, timedelta
import smtplib, pytz, time, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# -----------------------------
# CONFIGURATION
# -----------------------------
DB_NAME = "reminders.db"
os.environ["REMINDER_EMAIL"] = "nanpil02@gmail.com"  # your email
os.environ["REMINDER_PASS"] = "rvctchdyoiyjfona"  # app password
IST = pytz.timezone("Asia/Kolkata")

# Track sent reminders to prevent duplicates
sent_reminders = set()


# -----------------------------
# EMAIL SENDING FUNCTION
# -----------------------------
def send_email(recipient, subject, body):
    sender = os.environ["REMINDER_EMAIL"]
    password = os.environ["REMINDER_PASS"]

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
        print(f"✅ Email sent to {recipient}")
    except Exception as e:
        print(f"❌ Error sending email to {recipient}: {e}")


# -----------------------------
# DATABASE READER
# -----------------------------
def fetch_data():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT name, email FROM students")
    students = cursor.fetchall()

    cursor.execute("SELECT session_name, date, time FROM classes")
    classes = cursor.fetchall()

    cursor.execute("SELECT subject, due_date FROM assignments")
    assignments = cursor.fetchall()

    conn.close()
    return students, classes, assignments


# -----------------------------
# REMINDER LOGIC
# -----------------------------
def send_reminders():
    global sent_reminders
    students, classes, assignments = fetch_data()
    now = datetime.now(IST)
    print(f"⏰ Checking reminders at {now.strftime('%Y-%m-%d %H:%M:%S')} IST")

    # Class reminders
    for session_name, date_str, time_str in classes:
        class_time = IST.localize(
            datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        )
        for hours_before in [24, 1]:
            reminder_time = class_time - timedelta(hours=hours_before)
            key = f"class-{session_name}-{hours_before}"  # unique key
            # Check within a 10-minute window and not sent already
            if (
                0 <= (now - reminder_time).total_seconds() < 600
                and key not in sent_reminders
            ):
                for name, email in students:
                    body = (
                        f"Hi {name},\n\nReminder: Your class '{session_name}' "
                        f"is scheduled at {class_time.strftime('%I:%M %p on %d-%b-%Y')}.\n"
                        f"This is your {hours_before}-hour reminder.\n\n- Automated Reminder System"
                    )
                    send_email(
                        email,
                        f"Class Reminder: {session_name} ({hours_before}h before)",
                        body,
                    )
                sent_reminders.add(key)

    # Assignment reminders
    for subject, due_str in assignments:
        if len(due_str.strip()) == 10:  # add default time if missing
            due_str += " 09:00"
        due_time = IST.localize(datetime.strptime(due_str, "%Y-%m-%d %H:%M"))
        for hours_before in [24, 1]:
            reminder_time = due_time - timedelta(hours=hours_before)
            key = f"assignment-{subject}-{hours_before}"
            if (
                0 <= (now - reminder_time).total_seconds() < 600
                and key not in sent_reminders
            ):
                for name, email in students:
                    body = (
                        f"Hi {name},\n\nReminder: Your assignment '{subject}' "
                        f"is due at {due_time.strftime('%I:%M %p on %d-%b-%Y')}.\n"
                        f"This is your {hours_before}-hour reminder.\n\n- Automated Reminder System"
                    )
                    send_email(
                        email,
                        f"Assignment Reminder: {subject} ({hours_before}h before)",
                        body,
                    )
                sent_reminders.add(key)


# -----------------------------
# MAIN SCHEDULER LOOP
# -----------------------------
if __name__ == "__main__":
    print("🕒 Reminder Scheduler Started... (Checking every minute)")
    while True:
        send_reminders()
        time.sleep(60)




# email_reminder.py
import sqlite3
from datetime import datetime, timedelta
import smtplib, pytz, time, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# -----------------------------
# CONFIGURATION
# -----------------------------
DB_NAME = "reminders.db"  # path to your DB
os.environ["REMINDER_EMAIL"] = "nanpil02@gmail.com"  # your email
os.environ["REMINDER_PASS"] = "rvctchdyoiyjfona"  # app password
IST = pytz.timezone("Asia/Kolkata")

# Track sent reminders to prevent duplicates (in-memory)
sent_reminders = set()

# -----------------------------
# EMAIL SENDING FUNCTION
# -----------------------------
def send_email(recipient, subject, body):
    sender = os.environ["REMINDER_EMAIL"]
    password = os.environ["REMINDER_PASS"]

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
        print(f"✅ Email sent to {recipient}")
        return True
    except Exception as e:
        print(f"❌ Error sending email to {recipient}: {e}")
        return False

# -----------------------------
# DATABASE READER
# -----------------------------
def fetch_data():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # students must include id, name, email, discord_id, course_id
    cursor.execute("SELECT id, name, email, discord_id, course_id FROM students")
    students = cursor.fetchall()

    cursor.execute("SELECT id, course_id, session_name, date, time FROM classes")
    classes = cursor.fetchall()

    cursor.execute("SELECT id, course_id, subject, due_date FROM assignments")
    assignments = cursor.fetchall()

    conn.close()
    return students, classes, assignments

# -----------------------------
# LOG REMINDER FUNCTION  (paste here)
# -----------------------------
def log_reminder(student_id, reminder_type, status):
    """Log reminder result into reminder_status table.
    status = 'Sent' or 'Not Sent'
    """
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

# -----------------------------
# REMINDER LOGIC
# -----------------------------
def send_reminders():
    global sent_reminders
    students, classes, assignments = fetch_data()
    now = datetime.now(IST)
    print(f"⏰ Checking reminders at {now.strftime('%Y-%m-%d %H:%M:%S')} IST")

    # Convert students list to dict for quick lookup by id
    student_dict = {s[0]: s for s in students}  # id -> (id, name, email, discord_id, course_id)

    # Class reminders
    for class_row in classes:
        class_id, course_id, session_name, date_str, time_str = class_row
        try:
            class_time = IST.localize(datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M"))
        except Exception:
            continue
        for hours_before in [24, 1]:
            reminder_time = class_time - timedelta(hours=hours_before)
            key = f"class-{class_id}-{hours_before}"
            # Check within a 10-minute window and not sent already
            if 0 <= (now - reminder_time).total_seconds() < 600 and key not in sent_reminders:
                # send to students who belong to the same course (match course_id)
                for s in students:
                    student_id, name, email, discord_id, s_course_id = s
                    if s_course_id == course_id:
                        body = (
                            f"Hi {name},\n\nReminder: Your class '{session_name}' "
                            f"is scheduled at {class_time.strftime('%I:%M %p on %d-%b-%Y')}.\n"
                            f"This is your {hours_before}-hour reminder.\n\n- Automated Reminder System"
                        )
                        ok = send_email(email, f"Class Reminder: {session_name} ({hours_before}h before)", body)
                        log_reminder(student_id, "email", "Sent" if ok else "Not Sent")
                sent_reminders.add(key)

    # Assignment reminders
    for assignment_row in assignments:
        assignment_id, course_id, subject, due_str = assignment_row
        if len(due_str.strip()) == 10:  # add default time if missing
            due_str += " 09:00"
        try:
            due_time = IST.localize(datetime.strptime(due_str, "%Y-%m-%d %H:%M"))
        except Exception:
            continue
        for hours_before in [24, 1]:
            reminder_time = due_time - timedelta(hours=hours_before)
            key = f"assignment-{assignment_id}-{hours_before}"
            if 0 <= (now - reminder_time).total_seconds() < 600 and key not in sent_reminders:
                for s in students:
                    student_id, name, email, discord_id, s_course_id = s
                    if s_course_id == course_id:
                        body = (
                            f"Hi {name},\n\nReminder: Your assignment '{subject}' "
                            f"is due at {due_time.strftime('%I:%M %p on %d-%b-%Y')}.\n"
                            f"This is your {hours_before}-hour reminder.\n\n- Automated Reminder System"
                        )
                        ok = send_email(email, f"Assignment Reminder: {subject} ({hours_before}h before)", body)
                        log_reminder(student_id, "email", "Sent" if ok else "Not Sent")
                sent_reminders.add(key)

# -----------------------------
# MAIN SCHEDULER LOOP
# -----------------------------
if __name__ == "__main__":
    print("🕒 Reminder Scheduler Started... (Checking every minute)")
    while True:
        send_reminders()
        time.sleep(60)
