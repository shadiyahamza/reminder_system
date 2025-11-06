# import sqlite3

# conn = sqlite3.connect("data/reminders.db")
# cursor = conn.cursor()
# cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
# print(cursor.fetchall())
# conn.close()
import sqlite3

conn = sqlite3.connect("data/reminders.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM courses")
print(cursor.fetchall())
conn.close()
