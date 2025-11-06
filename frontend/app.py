import streamlit as st
import sqlite3
import os
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# -------------------------------
# DATABASE SETUP
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "../data/reminders.db")

def get_connection():
    # Safe SQLite connection
    return sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)

# Create table if it doesn't exist
with get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            remind_time TEXT NOT NULL,
            email_sent TEXT DEFAULT 'Pending'
        )
    """)
    conn.commit()

# -------------------------------
# FUNCTIONS
# -------------------------------
def add_reminder(title, message, remind_time):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO reminders (title, message, remind_time) VALUES (?, ?, ?)",
            (title, message, remind_time)
        )
        conn.commit()
    st.success("Reminder added!")
    st.rerun()
    # st.experimental_user()  # Refresh the app

def get_reminders():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, message, remind_time, email_sent FROM reminders ORDER BY remind_time ASC")
        return cursor.fetchall()

def delete_reminder(reminder_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reminders WHERE id=?", (reminder_id,))
        conn.commit()
    st.success("Reminder deleted!")
    st.rerun()
    # st.experimental_user()

def send_email(to_email, subject, body):
    sender_email = os.environ.get("REMINDER_EMAIL")
    sender_pass = os.environ.get("REMINDER_PASS")

    if not sender_email or not sender_pass:
        st.error("Email credentials not set in environment variables!")
        return

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_pass)
        server.send_message(msg)
        server.quit()
        st.success(f"Email sent to {to_email}")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# -------------------------------
# FRONTEND
# -------------------------------
st.title("📌 Automated Reminder App")
menu = ["View Reminders", "View Students", "Add Reminder"]
# choice = st.sidebar.radio("Menu", menu)
choice = st.selectbox("Menu", menu, index=0)
if choice == "Add Reminder":
    st.subheader("Add a new reminder")
    title = st.text_input("Title")
    message = st.text_area("Message")
    remind_time = st.date_input("Remind at", datetime.now() + timedelta(minutes=5))

    if st.button("Add Reminder"):
        if title.strip() and message.strip():
            add_reminder(title, message, remind_time.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            st.error("Please fill all fields!")

elif choice == "View Reminders":
    st.subheader("View reminders by course")

    # Fetch distinct courses from reminders (assuming 'title' represents course)
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM courses ORDER BY course_name ASC")
        courses = cursor.fetchall()
        courses = [course[1] for course in courses]  # Extract course names

    if courses:
        selected_course = st.selectbox("Select a course", courses)

        # Fetch reminders for selected course
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, message, remind_time, email_sent FROM reminders WHERE title=? ORDER BY remind_time ASC",
                (selected_course,)
            )
            course_reminders = cursor.fetchall()

        if course_reminders:
            for reminder in course_reminders:
                id_, title, message, remind_time, email_sent = reminder
                col1, col2, col3 = st.columns([3, 5, 2])
                with col1:
                    st.markdown(f"**{title}**")
                    st.write(message)
                with col2:
                    st.markdown(f"⏰ {remind_time}")
                with col3:
                    email_color = "green" if email_sent == "Sent" else "orange"
                    st.markdown(f"<span style='color:{email_color}; font-weight:bold'>{email_sent}</span>", unsafe_allow_html=True)
                    if st.button("Delete", key=f"del_{id_}"):
                        delete_reminder(id_)
        else:
            st.info(f"No reminders found for course: {selected_course}")
    else:
        st.info("No courses found in reminders.")
elif choice == "View Students":
    st.subheader("Enrolled Students")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email FROM students ORDER BY name ASC")
        students = cursor.fetchall()
        if students:
            for student in students:
                id_, name, email = student
                st.markdown(f"**{name}** - {email}")
        else:
            st.info("No students enrolled yet.")

# -------------------------------
# OPTIONAL: Auto-send due emails
# -------------------------------
# Example: This runs on every rerun. You can implement background scheduling with APScheduler or Cron.
current_time = datetime.now()
for reminder in get_reminders():
    id_, title, message, remind_time_str, email_sent = reminder
    remind_time_dt = datetime.strptime(remind_time_str, "%Y-%m-%d %H:%M:%S")
    if current_time >= remind_time_dt and email_sent != "Sent":
        # send_email("recipient@example.com", title, message)  # <-- Replace with actual email
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE reminders SET email_sent='Sent' WHERE id=?", (id_,))
            conn.commit()
        st.info(f"Reminder '{title}' marked as Sent.")

