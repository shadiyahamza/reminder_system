-- run in sqlite3 or use a Python script to execute these
CREATE TABLE IF NOT EXISTS courses (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  course_name TEXT,
  mode TEXT,
  batch TEXT
);

CREATE TABLE IF NOT EXISTS students (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  email TEXT,
  discord_id TEXT,
  course_id INTEGER,
  FOREIGN KEY (course_id) REFERENCES courses(id)
);

CREATE TABLE IF NOT EXISTS classes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  course_id INTEGER,
  session_name TEXT,
  date TEXT,     -- YYYY-MM-DD
  time TEXT,     -- HH:MM (24h)
  FOREIGN KEY (course_id) REFERENCES courses(id)
);

CREATE TABLE IF NOT EXISTS assignments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  course_id INTEGER,
  subject TEXT,
  due_date TEXT,  -- YYYY-MM-DD or YYYY-MM-DD HH:MM
  FOREIGN KEY (course_id) REFERENCES courses(id)
);

-- reminder_status will be auto-created by the function if missing,
-- but you can create it manually if you prefer:
CREATE TABLE IF NOT EXISTS reminder_status (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  student_id INTEGER,
  reminder_type TEXT,
  reminder_time TEXT,
  status TEXT,
  sent_date TEXT,
  FOREIGN KEY (student_id) REFERENCES students(id)
);
