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

def get_profile(user_id):
    cursor.execute(
        """
        SELECT balance, xp, level, last_daily,
               last_mine, wins
        FROM plats
        WHERE user_id=?
        """,
        (user_id,)
    )

    row = cursor.fetchone()

    if row:
        return row

    cursor.execute(
        """
        INSERT INTO plats(user_id)
        VALUES(?)
        """,
        (user_id,)
    )

    conn.commit()

    return (0,0,1,0,0,0)

def update_mine(user_id, balance, xp, level, last_mine):

    cursor.execute("""
    UPDATE plats
    SET balance=?,
        xp=?,
        level=?,
        last_mine=?
    WHERE user_id=?
    """,
    (balance, xp, level, last_mine, user_id))

    conn.commit()

def update_daily(user_id, balance, last_daily):

    cursor.execute("""
    UPDATE plats
    SET balance=?,
        last_daily=?
    WHERE user_id=?
    """,
    (balance, last_daily, user_id))

    conn.commit()
