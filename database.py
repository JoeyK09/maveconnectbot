import sqlite3

conn = sqlite3.connect("maveconnect.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS plats (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0
)
""")

conn.commit()
