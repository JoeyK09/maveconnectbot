import os
import psycopg2
from config import PICKAXES

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL not found")


def get_connection():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    return conn


def get_cursor():
    conn = get_connection()
    return conn, conn.cursor()

conn, cursor = get_cursor()

# ================= CREATE TABLE =================

PICKAXES = {
    1: {"name": "Wood", "price": 0, "bonus": 0},
    2: {"name": "Stone", "price": 500, "bonus": 5},
    3: {"name": "Bronze", "price": 2000, "bonus": 10},
    4: {"name": "Iron", "price": 5000, "bonus": 20},
    5: {"name": "Gold", "price": 10000, "bonus": 35},
    6: {"name": "Diamond", "price": 25000, "bonus": 50},
}

cursor.execute("""
CREATE TABLE IF NOT EXISTS plats(
    user_id TEXT PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    pickaxe INTEGER DEFAULT 1,
    last_daily BIGINT DEFAULT 0,
    last_mine BIGINT DEFAULT 0,
    wins INTEGER DEFAULT 0,
    streak INTEGER DEFAULT 0,
    referred_by TEXT,
    mining_bonus INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS favorites(
    user_id TEXT,
    coin TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS alerts(
    user_id TEXT NOT NULL,
    coin TEXT NOT NULL,
    target DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS achievements(
    user_id TEXT,
    achievement TEXT,
    PRIMARY KEY(user_id, achievement)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS deposits(
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    coin TEXT NOT NULL,
    network TEXT NOT NULL,
    txid TEXT NOT NULL,
    amount DOUBLE PRECISION NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS withdrawals(
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    amount INTEGER NOT NULL,
    phone TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions(
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    type TEXT NOT NULL,
    amount DOUBLE PRECISION NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")


cursor.execute("DROP TABLE IF EXISTS deposits")

cursor.execute("""
CREATE TABLE deposits(
    id SERIAL PRIMARY KEY,
    user_id TEXT,
    coin TEXT,
    network TEXT,
    txid TEXT,
    amount DOUBLE PRECISION,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()

# ================= FUNCTIONS =================

def get_profile(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT balance, xp, level, pickaxe,
               last_daily, last_mine, wins,streak
        FROM plats
        WHERE user_id=%s
    """, (user_id,))

    row = cursor.fetchone()

    if not row:
        cursor.execute(
            "INSERT INTO plats(user_id) VALUES(%s)",
            (user_id,)
        )

        row = (0, 0, 1, 1, 0, 0, 0, 0)

    cursor.close()
    conn.close()

    return row
    

def get_balance(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT balance FROM plats WHERE user_id=%s",
        (user_id,)
    )

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    return row[0] if row else 0
    

def add_plats(user_id, amount):
    conn = get_connection()
    cursor = conn.cursor()

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

    cursor.close()
    conn.close()


def remove_plats(user_id, amount):
    conn = get_connection()
    cursor = conn.cursor()

    balance = get_balance(user_id)
    new_balance = max(0, balance - amount)

    cursor.execute("""
        UPDATE plats
        SET balance=%s
        WHERE user_id=%s
    """, (
        new_balance,
        user_id
    ))

    conn.commit()
    cursor.close()
    conn.close()


def update_mine(user_id, balance, xp, level, pickaxe, last_mine):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE plats
        SET balance=%s,
            xp=%s,
            level=%s,
            pickaxe=%s,
            last_mine=%s
        WHERE user_id=%s
    """, (
        balance,
        xp,
        level,
        pickaxe,
        last_mine,
        user_id
    ))

    conn.commit()
    cursor.close()
    conn.close()


def update_pickaxe(user_id, balance, pickaxe):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE plats
        SET balance=%s,
            pickaxe=%s
        WHERE user_id=%s
    """, (
        balance,
        pickaxe,
        user_id
    ))

    conn.commit()
    cursor.close()
    conn.close()


def update_daily(user_id, balance, last_daily):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE plats
        SET balance=%s,
            last_daily=%s
            streak=%s
        WHERE user_id=%s
    """, (
        balance,
        last_daily,
        streak,
        user_id
    ))

    conn.commit()
    cursor.close()
    conn.close()
    

def add_win(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE plats
        SET wins = wins + 1
        WHERE user_id=%s
    """, (user_id,))

    conn.commit()
    cursor.close()
    conn.close()
    

def leaderboard(limit=10):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT user_id, balance
        FROM plats
        ORDER BY balance DESC
        LIMIT %s
    """, (limit,))

    rows = cursor.fetchall()

    conn.commit()
    cursor.close()
    conn.close()

    return rows
    

def add_favorite(user, coin):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT 1
        FROM favorites
        WHERE user_id=%s
        AND coin=%s
        """,
        (user, coin)
    )

    if cursor.fetchone():
        return

    cursor.execute(
        """
        INSERT INTO favorites(user_id, coin)
        VALUES(%s, %s)
        """,
        (user, coin)
    )

    conn.commit()
    cursor.close()
    conn.close()
    

def get_favorites(user):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT coin FROM favorites WHERE user_id=%s",
        (user,)
    )
    return [x[0] for x in cursor.fetchall()]


def add_alert(user, coin, target):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO alerts VALUES (%s,%s,%s)",
        (user, coin, target)
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_alerts():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT user_id, coin, target FROM alerts"
    )
    return cursor.fetchall()


def delete_alert(user, coin, target):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM alerts WHERE user_id=%s AND coin=%s AND target=%s",
        (user, coin, target)
    )
    conn.commit()
    cursor.close()
    conn.close()
    
    
def has_achievement(user_id, achievement):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 1 FROM achievements
        WHERE user_id=%s AND achievement=%s
    """, (user_id, achievement))

    found = cursor.fetchone() is not None

    cursor.close()
    conn.close()

    return found

def unlock_achievement(user_id, achievement):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO achievements(user_id, achievement)
        VALUES(%s, %s)
        ON CONFLICT DO NOTHING
    """, (user_id, achievement))

    cursor.close()
    conn.close()


def get_pickaxe(user_id):
    get_profile(user_id)

    cursor.execute(
        "SELECT pickaxe FROM plats WHERE user_id=%s",
        (user_id,)
    )

    row = cursor.fetchone()

    pickaxe = row[0] if row else 1
    return pickaxe


def get_mining_bonus(user_id):
    get_profile(user_id)

    cursor.execute(
        "SELECT mining_bonus FROM plats WHERE user_id=%s",
        (user_id,)
    )

    row = cursor.fetchone()

    return row[0] if row else 0


def get_mining_bonus(user):
    balance, xp, level, pickaxe, last_daily, last_mine, wins, streak = get_profile(user)

    return PICKAXES[pickaxe]["bonus"]


def create_deposit(user_id, coin, network, txid, amount):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO deposits
        (user_id, coin, network, txid, amount)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        user_id,
        coin,
        network,
        txid,
        amount
    ))

    conn.commit()
    cursor.close()
    conn.close()


def add_withdrawal(user_id, amount, phone):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO withdrawals(user_id, amount, phone)
        VALUES(%s, %s, %s)
    """, (
        user_id,
        amount,
        phone
    ))

    conn.commit()
    cursor.close()
    conn.close()


def get_pending_withdrawals():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, user_id, amount, phone
        FROM withdrawals
        WHERE status='pending'
        ORDER BY id
    """)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows


def add_deposit(user_id, coin, txid):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO deposits(user_id, coin, txid)
        VALUES(%s, %s, %s)
    """, (
        user_id,
        coin,
        txid
    ))

    conn.commit()
    cursor.close()
    conn.close()


def get_pending_deposits():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, user_id, coin, txid
        FROM deposits
        WHERE status='pending'
        ORDER BY id
    """)

    rows = cursor.fetchall()

    conn.commit()
    cursor.close()
    conn.close()

    return rows

    
