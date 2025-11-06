import sqlite3
import pandas as pd
from datetime import datetime, timedelta

DB_PATH = r"C:\Users\shadiya\Downloads\automated_reminders\automated_reminders\database\reminders.db"

print("\n=== Classes ===")
classes = pd.read_sql_query("SELECT * FROM classes", conn)
print(classes.head())

print("\n=== Upcoming classes only ===")
now = datetime.now()
for _, row in classes.iterrows():
    try:
        dt = datetime.strptime(f"{row['date']} {row['time']}", "%Y-%m-%d %H:%M")
        if dt > now:
            print(f"✅ {row['course']} - {row['session_name']} at {dt}")
    except Exception as e:
        print(f"⚠️ {row['course']} - invalid date/time → {e}")
