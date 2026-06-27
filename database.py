import os
import psycopg2

# ================= DATABASE CONNECTION =================

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL not found")

conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cursor = conn.cursor()

# ================= CREATE TABLE =================

cursor.execute("""
CREATE TABLE IF NOT EXISTS plats(
    user_id TEXT PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    last_daily BIGINT DEFAULT 0,
    last_mine BIGINT DEFAULT 0,
    wins INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS favorites(
    user_id TEXT,
    coin TEXT,
    PRIMARY KEY(user_id, coin)
)
""")
conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS alerts(
    user_id TEXT,
    coin TEXT,
    target REAL
)
""")
conn.commit()

# ================= FUNCTIONS =================

def get_profile(user_id):
    cursor.execute("""
        SELECT balance,
               xp,
               level,
               last_daily,
               last_mine,
               wins
        FROM plats
        WHERE user_id=%s
    """, (user_id,))

    row = cursor.fetchone()

    if row:
        return row

    cursor.execute("""
        INSERT INTO plats(user_id)
        VALUES(%s)
    """, (user_id,))

    return (0, 0, 1, 0, 0, 0)


def get_balance(user_id):
    cursor.execute(
        "SELECT balance FROM plats WHERE user_id=%s",
        (user_id,)
    )

    row = cursor.fetchone()

    return row[0] if row else 0


def add_plats(user_id, amount):
    balance = get_balance(user_id)

    cursor.execute("""
        INSERT INTO plats(user_id, balance)
        VALUES(%s, %s)
        ON CONFLICT (user_id)
        DO UPDATE SET balance=%s
    """, (
        user_id,
        balance + amount,
        balance + amount
    ))


def remove_plats(user_id, amount):
    get_profile(user_id)
    
    balance = get_balance(user_id)

    new_balance = max(0, balance - amount)

    cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_balance
ON plats(balance DESC)
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_level
ON plats(level DESC)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS vip_users(
    user_id TEXT PRIMARY KEY,
    expires BIGINT
)
""")

cursor.execute("""
ALTER TABLE plats
ADD COLUMN IF NOT EXISTS referred_by TEXT;
""")

def update_mine(user_id, balance, xp, level, last_mine):
    get_profile(user_id)

    cursor.execute("""
        UPDATE plats
        SET balance=%s,
            xp=%s,
            level=%s,
            last_mine=%s
        WHERE user_id=%s
    """, (
        balance,
        xp,
        level,
        last_mine,
        user_id
    ))


def update_daily(user_id, balance, last_daily):
    get_profile(user_id)
    
    cursor.execute("""
        UPDATE plats
        SET balance=%s,
            last_daily=%s
        WHERE user_id=%s
    """, (
        balance,
        last_daily,
        user_id
    ))


def add_win(user_id):
    get_profile(user_id)
    
    cursor.execute("""
        UPDATE plats
        SET wins = wins + 1
        WHERE user_id=%s
    """, (user_id,))


def leaderboard(limit=10):
    cursor.execute("""
        SELECT user_id, balance
        FROM plats
        ORDER BY balance DESC
        LIMIT %s
    """, (limit,))

    return cursor.fetchall()

def add_favorite(user, coin):
    cursor.execute(
        "INSERT OR IGNORE INTO favorites(user_id, coin) VALUES(?, ?)",
        (user, coin)
    )
    conn.commit()


def get_favorites(user):
    cursor.execute(
        "SELECT coin FROM favorites WHERE user_id=?",
        (user,)
    )
    return [row[0] for row in cursor.fetchall()]
    
def add_alert(user, coin, target):
    cursor.execute(
        "INSERT INTO alerts(user_id, coin, target) VALUES(?,?,?)",
        (user, coin, target)
    )
    conn.commit()


def get_alerts():
    cursor.execute(
        "SELECT user_id, coin, target FROM alerts"
    )
    return cursor.fetchall()


def delete_alert(user, coin, target):
    cursor.execute(
        "DELETE FROM alerts WHERE user_id=? AND coin=? AND target=?",
        (user, coin, target)
    )
    conn.commit()
