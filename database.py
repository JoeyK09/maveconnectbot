import sqlite3

conn = sqlite3.connect("plats.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS plats (
    user_id TEXT PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    last_daily INTEGER DEFAULT 0,
    last_mine INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0
)
""")

conn.commit()


def get_balance(user_id):
    cursor.execute(
        "SELECT balance FROM plats WHERE user_id=?",
        (user_id,)
    )
    row = cursor.fetchone()
    return row[0] if row else 0


def add_plats(user_id, amount):
    balance = get_balance(user_id)

    if balance == 0:
        cursor.execute(
            "INSERT OR IGNORE INTO plats(user_id, balance) VALUES(?, ?)",
            (user_id, amount)
        )
    else:
        cursor.execute(
            "UPDATE plats SET balance=? WHERE user_id=?",
            (balance + amount, user_id)
        )

    conn.commit()
