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
ALTER TABLE plats
ADD COLUMN IF NOT EXISTS vip BOOLEAN DEFAULT FALSE
""")

cursor.execute("""
ALTER TABLE plats
ADD COLUMN IF NOT EXISTS vip_plan TEXT DEFAULT 'Free'
""")

cursor.execute("""
ALTER TABLE plats
ADD COLUMN IF NOT EXISTS vip_start TIMESTAMP
""")

cursor.execute("""
ALTER TABLE plats
ADD COLUMN IF NOT EXISTS vip_expiry TIMESTAMP
""")

cursor.execute("""
ALTER TABLE deposits
ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP
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

cursor.execute("""
CREATE TABLE IF NOT EXISTS crypto_withdrawals(
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    coin TEXT NOT NULL,
    network TEXT NOT NULL,
    address TEXT NOT NULL,
    amount DOUBLE PRECISION NOT NULL,
    status TEXT DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS vip_payments(
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    plan TEXT NOT NULL,
    amount DOUBLE PRECISION NOT NULL,
    method TEXT NOT NULL,
    reference TEXT,
    status TEXT DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

def create_vip_tables():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS vip_subscriptions (
        user_id BIGINT PRIMARY KEY,
        plan TEXT,
        start_date TIMESTAMP,
        expiry_date TIMESTAMP,
        active BOOLEAN DEFAULT TRUE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS vip_payments (
        id SERIAL PRIMARY KEY,
        user_id BIGINT,
        plan TEXT,
        amount INTEGER,
        payment_method TEXT,
        reference TEXT UNIQUE,
        status TEXT DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    cur.close()
    conn.close()

def save_vip_payment(user_id, plan, amount, payment_method, reference):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO vip_payments
    (user_id, plan, amount, payment_method, reference)
    VALUES (%s,%s,%s,%s,%s)
    """, (
        user_id,
        plan,
        amount,
        payment_method,
        reference
    ))

    conn.commit()
    cur.close()
    conn.close()

def activate_vip(user_id, plan, expiry):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO vip_subscriptions
    (user_id, plan, start_date, expiry_date, active)

    VALUES (%s,%s,NOW(),%s,TRUE)

    ON CONFLICT(user_id)

    DO UPDATE SET

    plan=EXCLUDED.plan,
    start_date=NOW(),
    expiry_date=EXCLUDED.expiry_date,
    active=TRUE
    """, (
        user_id,
        plan,
        expiry
    ))

    conn.commit()
    cur.close()
    conn.close()

def is_vip(user_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT active
    FROM vip_subscriptions
    WHERE user_id=%s
    """, (user_id,))

    row = cur.fetchone()

    cur.close()
    conn.close()

    return row and row[0]

def get_vip_info(user_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT
    active,
    plan,
    start_date,
    expiry_date

    FROM vip_subscriptions

    WHERE user_id=%s
    """, (user_id,))

    row = cur.fetchone()

    cur.close()
    conn.close()

    return row

def get_vip_payment_history(user_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT
    plan,
    amount,
    payment_method,
    status,
    created_at

    FROM vip_payments

    WHERE user_id=%s

    ORDER BY created_at DESC
    """, (user_id,))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows


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

    
def credit_balance(user_id, amount):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE plats
        SET balance = balance + %s
        WHERE user_id = %s
    """, (amount, user_id))

    conn.commit()
    cursor.close()
    conn.close()

def txid_exists(txid):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 1
        FROM deposits
        WHERE txid = %s
        LIMIT 1
    """, (txid,))

    exists = cursor.fetchone() is not None

    cursor.close()
    conn.close()

    return exists

def update_deposit_status(txid, status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE deposits
        SET status=%s,
            approved_at=CURRENT_TIMESTAMP
        WHERE txid=%s
    """, (status, txid))

    conn.commit()
    cursor.close()
    conn.close()


def add_transaction(user_id, tx_type, amount, description):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO transactions
        (user_id, type, amount, description)
        VALUES (%s, %s, %s, %s)
    """, (
        user_id,
        tx_type,
        amount,
        description
    ))

    conn.commit()
    cursor.close()
    conn.close()


def add_crypto_withdrawal(user_id, coin, network, address, amount):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO crypto_withdrawals
        (user_id, coin, network, address, amount)
        VALUES (%s,%s,%s,%s,%s)
    """, (
        user_id,
        coin,
        network,
        address,
        amount
    ))

    conn.commit()

    cursor.close()
    conn.close()


def is_vip(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT vip, vip_expiry
        FROM plats
        WHERE user_id=%s
    """, (user_id,))

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if not row:
        return False

    vip, expiry = row

    if not vip:
        return False

    if expiry and expiry < datetime.now():
        remove_vip(user_id)
        return False

    return True


def activate_vip(user_id, plan, expiry):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE plats
        SET
            vip=TRUE,
            vip_plan=%s,
            vip_start=NOW(),
            vip_expiry=%s
        WHERE user_id=%s
    """, (
        plan,
        expiry,
        user_id
    ))

    conn.commit()

    cursor.close()
    conn.close()


def remove_vip(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE plats
        SET
            vip=FALSE,
            vip_plan='Free',
            vip_start=NULL,
            vip_expiry=NULL
        WHERE user_id=%s
    """, (user_id,))

    conn.commit()

    cursor.close()
    conn.close()


def get_vip_info(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT vip,
               vip_plan,
               vip_start,
               vip_expiry
        FROM plats
        WHERE user_id=%s
    """, (user_id,))

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    return row


def save_vip_payment(user_id, plan, amount, method, reference):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO vip_payments
        (user_id, plan, amount, method, reference)
        VALUES(%s,%s,%s,%s,%s)
    """, (
        user_id,
        plan,
        amount,
        method,
        reference
    ))

    conn.commit()

    cursor.close()
    conn.close()

