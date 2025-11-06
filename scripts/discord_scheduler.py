# discord_scheduler.py
import os
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

# === Load environment variables ===
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# === Configuration ===
DB_PATH = r"D:\Internship_ICT\duplicate\automated_reminders\database\reminders.db"
CHANNEL_NAME = "ClassReminderBot"  # 👈 your channel name
TEST_MODE = False  # ✅ True = quick testing (1–2 mins before instead of 24h/1h)

# === Discord client setup ===
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
client = discord.Client(intents=intents)

# === Database helper ===
def connect_db():
    return sqlite3.connect(DB_PATH)

def fetch_table(name):
    conn = connect_db()
    df = pd.read_sql_query(f"SELECT * FROM {name}", conn)
    conn.close()
    return df

# === Discord send helper ===
async def send_to_channel(message):
    """Send a message only to the #class-reminder channel."""
    for guild in client.guilds:
        for channel in guild.text_channels:
            if channel.name.lower() == CHANNEL_NAME.lower():
                try:
                    await channel.send(message)
                    print(f"✅ Sent reminder in #{CHANNEL_NAME}")
                    return
                except Exception as e:
                    print(f"⚠️ Could not send to #{CHANNEL_NAME}: {e}")
    print(f"⚠️ Channel '{CHANNEL_NAME}' not found in any guild.")

# === Reminder functions ===
async def send_class_reminder(course, session_name, date_str, time_str, hours_before):
    msg = (
        f"⏰ **Class Reminder:** {course} - {session_name} starts in {hours_before} hour(s)!\n"
        f"🗓️ Date: {date_str} | 🕘 Time: {time_str}"
    )
    await send_to_channel(msg)

async def send_assignment_reminder(course, subject, due_date):
    msg = (
        f"📝 **Assignment Reminder:** Assignment **{subject}** for **{course}** "
        f"is due tomorrow! 📅 ({due_date})"
    )
    await send_to_channel(msg)

# === Scheduler setup ===
@client.event
async def on_ready():
    print(f"🤖 Logged in as {client.user}")
    scheduler = AsyncIOScheduler()
    now = datetime.now()

    # === Schedule class reminders ===
    try:
        classes = fetch_table("classes")
    except Exception as e:
        print(f"⚠️ Could not read 'classes' table: {e}")
        classes = pd.DataFrame()

    for _, row in classes.iterrows():
        try:
            class_time = datetime.strptime(f"{row['date']} {row['time']}", "%Y-%m-%d %H:%M")

            if TEST_MODE:
                reminder_24h = now + timedelta(minutes=1)
                reminder_1h = now + timedelta(seconds=30)
            else:
                reminder_24h = class_time - timedelta(hours=24)
                reminder_1h = class_time - timedelta(hours=1)

            if reminder_24h > now:
                scheduler.add_job(
                    send_class_reminder, "date",
                    run_date=reminder_24h,
                    args=[row["course"], row["session_name"], row["date"], row["time"], 24 if not TEST_MODE else 0.016]
                )

            if reminder_1h > now:
                scheduler.add_job(
                    send_class_reminder, "date",
                    run_date=reminder_1h,
                    args=[row["course"], row["session_name"], row["date"], row["time"], 1 if not TEST_MODE else 0.008]
                )

            print(f"🗓️ Scheduled class reminders for {row['course']} - {row['session_name']}")
        except Exception as e:
            print(f"⚠️ Error scheduling class reminder: {e}")

    # === Schedule assignment reminders ===
    try:
        assignments = fetch_table("assignments")
    except Exception as e:
        print(f"⚠️ Could not read 'assignments' table: {e}")
        assignments = pd.DataFrame()

    for _, row in assignments.iterrows():
        try:
            due_date = datetime.strptime(row["due_date"], "%Y-%m-%d")

            if TEST_MODE:
                reminder_time = now + timedelta(minutes=2)
            else:
                reminder_time = due_date - timedelta(days=1)

            if reminder_time > now:
                scheduler.add_job(
                    send_assignment_reminder, "date",
                    run_date=reminder_time,
                    args=[row["course"], row["subject"], row["due_date"]]
                )

            print(f"🗓️ Scheduled assignment reminder for {row['course']} - {row['subject']}")
        except Exception as e:
            print(f"⚠️ Error scheduling assignment reminder: {e}")

    # === Start scheduler ===
    scheduler.start()
    print("✅ Scheduler started successfully and waiting for reminders...")

client.run(DISCORD_TOKEN)




# discord_reminder.py
import os
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
import pytz

# Load env
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Configuration
DB_PATH = r"reminders.db"  # ensure same DB or give full path
CHANNEL_NAME = "ClassReminderBot"
TEST_MODE = False
IST = pytz.timezone("Asia/Kolkata")

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
client = discord.Client(intents=intents)

def connect_db():
    return sqlite3.connect(DB_PATH)

def fetch_table(name):
    conn = connect_db()
    df = pd.read_sql_query(f"SELECT * FROM {name}", conn)
    conn.close()
    return df

# ---------- log_reminder (same as email) ----------
def log_reminder(student_id, reminder_type, status):
    conn = sqlite3.connect(DB_PATH)
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

# Helper to find students for a course
def get_students_for_course(course_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, discord_id FROM students WHERE course_id = ?", (course_id,))
    rows = cur.fetchall()
    conn.close()
    return rows  # list of (id, name, email, discord_id)

async def send_to_channel(message):
    for guild in client.guilds:
        for channel in guild.text_channels:
            if channel.name.lower() == CHANNEL_NAME.lower():
                try:
                    await channel.send(message)
                    return True
                except Exception as e:
                    print(f"⚠️ Could not send to #{CHANNEL_NAME}: {e}")
                    return False
    print(f"⚠️ Channel '{CHANNEL_NAME}' not found in any guild.")
    return False

# Scheduler setup
@client.event
async def on_ready():
    print(f"🤖 Logged in as {client.user}")
    scheduler = AsyncIOScheduler()
    now = datetime.now(IST)

    # classes
    try:
        classes = fetch_table("classes")
    except Exception as e:
        print(f"⚠️ Could not read 'classes' table: {e}")
        classes = pd.DataFrame()

    for _, row in classes.iterrows():
        try:
            class_time = datetime.strptime(f"{row['date']} {row['time']}", "%Y-%m-%d %H:%M")
            # attach timezone
            class_time = IST.localize(class_time)

            if TEST_MODE:
                reminder_24h = now + timedelta(minutes=1)
                reminder_1h = now + timedelta(seconds=30)
            else:
                reminder_24h = class_time - timedelta(hours=24)
                reminder_1h = class_time - timedelta(hours=1)

            # schedule job for each reminder
            def make_job_send(course_id, course, session_name, date_str, time_str, hours_before):
                async def job():
                    message = (
                        f"⏰ **Class Reminder:** {course} - {session_name} starts in {hours_before} hour(s)!\n"
                        f"🗓️ Date: {date_str} | 🕘 Time: {time_str}"
                    )
                    ok = await send_to_channel(message)
                    # log for all students in that course
                    students = get_students_for_course(course_id)
                    for s in students:
                        student_id = s[0]
                        log_reminder(student_id, "discord", "Sent" if ok else "Not Sent")
                return job

            if reminder_24h > now:
                scheduler.add_job(make_job_send(row['course_id'], row.get('course', ''), row['session_name'], row['date'], row['time']), 'date', run_date=reminder_24h)

            if reminder_1h > now:
                scheduler.add_job(make_job_send(row['course_id'], row.get('course', ''), row['session_name'], row['date'], row['time']), 'date', run_date=reminder_1h)

            print(f"🗓️ Scheduled class reminders for {row['course'] if 'course' in row else row.get('course_id')} - {row['session_name']}")
        except Exception as e:
            print(f"⚠️ Error scheduling class reminder: {e}")

    # assignments
    try:
        assignments = fetch_table("assignments")
    except Exception as e:
        print(f"⚠️ Could not read 'assignments' table: {e}")
        assignments = pd.DataFrame()

    for _, row in assignments.iterrows():
        try:
            due_date = datetime.strptime(row["due_date"], "%Y-%m-%d")
            due_date = IST.localize(due_date)
            if TEST_MODE:
                reminder_time = now + timedelta(minutes=2)
            else:
                reminder_time = due_date - timedelta(days=1)

            async def job_assign(course_id, course, subject, due_date_str):
                message = (
                    f"📝 **Assignment Reminder:** Assignment **{subject}** for **{course}** is due tomorrow! 📅 ({due_date_str})"
                )
                ok = await send_to_channel(message)
                students = get_students_for_course(course_id)
                for s in students:
                    student_id = s[0]
                    log_reminder(student_id, "discord", "Sent" if ok else "Not Sent")

            if reminder_time > now:
                scheduler.add_job(job_assign, 'date', run_date=reminder_time, args=[row['course_id'], row.get('course', ''), row['subject'], row['due_date']])

            print(f"🗓️ Scheduled assignment reminder for {row.get('course', row['course_id'])} - {row['subject']}")
        except Exception as e:
            print(f"⚠️ Error scheduling assignment reminder: {e}")

    scheduler.start()
    print("✅ Scheduler started successfully and waiting for reminders...")

client.run(DISCORD_TOKEN)
from db_helpers import log_reminder

