import sqlite3
import os

# Path to your database
DB_PATH = os.path.join("C:/Users/shadiya/Downloads/automated_reminders/automated_reminders/data", "reminders.db")

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Add the 'email_status' column if it doesn't exist
try:
    cursor.execute("ALTER TABLE reminders ADD COLUMN email_status TEXT DEFAULT 'Pending'")
    print("✅ Column 'email_status' added successfully.")
except sqlite3.OperationalError:
    print("ℹ️ Column 'email_status' already exists.")

conn.commit()
conn.close()
