import json
import random
import os
import time
import requests
from flask import Flask
from threading import Thread
from database import conn, cursor
import telebot

# ================= BOT =================

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise Exception("BOT_TOKEN not found")

bot = telebot.TeleBot(TOKEN, threaded=True)
print("Telegram bot initialized")

app = Flask(__name__)

# ================= GROUPS =================

FREE_GROUP = "https://t.me/UltimateAvian"
VIP_GROUP = "https://t.me/UltimateAve"
VIP_CHANNEL = "@UltimateAve"
ADMIN_ID = 7988782705

# ================= COINS =================

COINS = {
    "btc": "bitcoin",
    "eth": "ethereum",
    "bnb": "binancecoin",
    "sol": "solana",
    "xrp": "ripple",
    "ada": "cardano",
    "doge": "dogecoin",
    "matic": "matic-network",
    "dot": "polkadot",
    "ltc": "litecoin",
    "trx": "tron",
    "avax": "avalanche-2",
    "shib": "shiba-inu",
    "link": "chainlink"
}

# ================= CACHE =================

import json

price_cache = {}
CACHE_TIME = 30
vip_users = set()

# ================= PLATS =================

if os.path.exists("plats.json"):
    with open("plats.json", "r") as f:
        plats = json.load(f)
else:
    plats = {}

def save_plats():
    with open("plats.json", "w") as f:
        json.dump(plats, f, indent=4)

import sqlite3

# ================= DATABASE =================

conn = sqlite3.connect("plats.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS plats (
    user_id TEXT PRIMARY KEY,
    balance INTEGER DEFAULT 0
)
""")

conn.commit()

# ================= DATABASE FUNCTIONS =================

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
    
# ================= PRICE ENGINE ===============

def get_price(coin):
    coin = coin.lower().strip()

    COINCAP_IDS = {
        "btc": "btc-bitcoin",
        "eth": "eth-ethereum",
        "bnb": "bnb-binance-coin",
        "sol": "sol-solana",
        "xrp": "xrp-xrp",
        "ada": "ada-cardano",
        "doge": "doge-dogecoin",
        "dot": "dot-polkadot",
        "ltc": "ltc-litecoin",
        "trx": "trx-tron",
        "avax": "avax-avalanche",
        "shib": "shib-shiba-inu",
        "link": "link-chainlink"
    }

    if coin not in COINCAP_IDS:
        return None

    # ===== CACHE CHECK =====
    now = time.time()

    if coin in price_cache:
        price, timestamp = price_cache[coin]

        if now - timestamp < CACHE_TIME:
            return price

    try:
        r = requests.get(
            f"https://api.coinpaprika.com/v1/tickers/{COINCAP_IDS[coin]}",
            timeout=10
        )

        if r.status_code == 200:
            data = r.json()
            price = float(data["quotes"]["USD"]["price"])

            # ===== SAVE TO CACHE =====
            price_cache[coin] = (price, now)

            return price

    except Exception as e:
        print("CoinPaprika error:", repr(e))

    return None

def safe_get_price(coin):
    for _ in range(3):
        try:
            price = get_price(coin)

            if price is not None:
                return price

        except Exception as e:
            print("Retry error:", e)

        time.sleep(1)

    return None
    
# ================= SIGNAL ENGINE =================

def get_signal(coin):

    price = safe_get_price(coin)

    if price is None:
        return None

    score = 60
    action = "⚪ HOLD"

    return {
        "price": price,
        "change": 0,
        "score": score,
        "action": action
    }

    
def is_vip(user_id):

    if user_id in vip_users:
        return True

    try:
        member = bot.get_chat_member(VIP_CHANNEL, user_id)

        return member.status in [
            "member",
            "administrator",
            "creator"
        ]

    except Exception as e:
        print("VIP check error:", e)
        return False
    
# ================= FLASK =================

@app.route("/")
def home():
    return "LEVEL 4 AI TRADING BOT 🚀"

# ================= COMMANDS =================

@bot.message_handler(commands=["start"])
def start(msg):
    bot.reply_to(
        msg,
        f"🚀 LEVEL 4 AI TRADING BOT\n\n"
        f"📢 Free Group:\n{FREE_GROUP}\n\n"
        f"💎 VIP Group:\n{VIP_GROUP}\n\n"
        f"Commands:\n"
        f"/price btc\n"
        f"/signal btc\n"
        f"/scan\n"
        f"/ping\n"
        f"/test"
    )
    
@bot.message_handler(commands=["ping"])
def ping(msg):
    bot.reply_to(msg, "🏓 Pong! Bot is alive.")

@bot.message_handler(commands=["test"])
def test(msg):
    bot.reply_to(msg, "🔥 BOT ONLINE AND WORKING")

@bot.message_handler(commands=["price"])
def price_cmd(msg):
    try:
        parts = msg.text.split()

        if len(parts) < 2:
            bot.reply_to(msg, "Usage: /price btc")
            return

        coin = parts[1].lower().strip()

        price = safe_get_price(coin)

        if price is not None:
            bot.reply_to(
                msg,
                f"💰 {coin.upper()} = ${price:,.4f}"
            )
        else:
            bot.reply_to(
                msg,
                "❌ Coin not found or price service unavailable."
            )

    except Exception as e:
        print("Price error:", repr(e))
        bot.reply_to(msg, "⚠️ Error getting price")

@bot.message_handler(commands=["signal"])
def signal_cmd(msg):

    if not is_vip(msg.from_user.id):
        bot.reply_to(
            msg,
            f"🔒 VIP ONLY FEATURE\n\n"
            f"Join VIP:\n{VIP_GROUP}"
        )
        return

    try:
        parts = msg.text.split()

        if len(parts) < 2:
            bot.reply_to(msg, "Usage: /signal btc")
            return

        coin = parts[1].lower().strip()

        result = get_signal(coin)

        if result is None:
            bot.reply_to(msg, "❌ Coin not found")
            return

        bot.reply_to(
            msg,
            f"🤖 {coin.upper()} SIGNAL\n\n"
            f"{result['action']}\n"
            f"💰 Price: ${result['price']:,.4f}\n"
            f"📈 24H Change: {result['change']:.2f}%\n"
            f"🔥 Strength: {result['score']}/100"
        )

    except Exception as e:
        print("Signal error:", repr(e))
        bot.reply_to(msg, "⚠️ Error generating signal")

@bot.message_handler(commands=["scan"])
def scan(msg):

    if not is_vip(msg.from_user.id):
        bot.reply_to(
            msg,
            f"🔒 VIP ONLY FEATURE\n\n"
            f"Join VIP:\n{VIP_GROUP}"
        )
        return

    bot.reply_to(msg, "🔍 Scanning market...")

    try:
        output = "📊 LEVEL 4 MARKET SCAN\n\n"

        SCAN_COINS = ["btc", "eth", "bnb", "sol", "xrp"]

        for coin in SCAN_COINS:
            result = get_signal(coin)

            if result:
                output += (
                    f"{coin.upper()} | "
                    f"{result['action']} | "
                    f"{result['score']}/100\n"
                )

        bot.send_message(msg.chat.id, output)

    except Exception as e:
        print("Scan error:", repr(e))
        bot.reply_to(msg, "⚠️ Scan failed")

@bot.message_handler(commands=["addvip"])
def addvip(msg):

    if msg.from_user.id != ADMIN_ID:
        return

    parts = msg.text.split()

    if len(parts) != 2:
        bot.reply_to(msg, "Usage: /addvip USER_ID")
        return

    try:
        user_id = int(parts[1])

        vip_users.add(user_id)

        bot.reply_to(
            msg,
            f"✅ Added {user_id} to VIP"
        )

    except Exception as e:
        bot.reply_to(msg, f"Error: {e}")

@bot.message_handler(commands=["removevip"])
def removevip(msg):

    if msg.from_user.id != ADMIN_ID:
        return

    parts = msg.text.split()

    if len(parts) != 2:
        bot.reply_to(msg, "Usage: /removevip USER_ID")
        return

    try:
        user_id = int(parts[1])

        vip_users.discard(user_id)

        bot.reply_to(
            msg,
            f"❌ Removed {user_id}"
        )

    except Exception as e:
        bot.reply_to(msg, f"Error: {e}")

@bot.message_handler(commands=["vipcount"])
def vipcount(msg):

    if msg.from_user.id != ADMIN_ID:
        return

    bot.reply_to(
        msg,
        f"💎 VIP Users: {len(vip_users)}"
    )

@bot.message_handler(commands=["nettest"])
def nettest(msg):
    try:
        r = requests.get("https://www.google.com", timeout=10)
        bot.reply_to(msg, f"Google OK: {r.status_code}")
    except Exception as e:
        bot.reply_to(msg, str(e))
        
@bot.message_handler(commands=["paprika"])
def paprika_test(msg):
    try:
        r = requests.get(
            "https://api.coinpaprika.com/v1/tickers/btc-bitcoin",
            timeout=10
        )

        bot.reply_to(
            msg,
            f"Status: {r.status_code}\n\n{r.text[:500]}"
        )

    except Exception as e:
        bot.reply_to(msg, f"Error: {e}")

@bot.message_handler(commands=["subscribe"])
def subscribe(msg):
    bot.reply_to(
        msg,
        "💎 VIP MEMBERSHIP\n\n"
        "Monthly: $10\n"
        "Quarterly: $25\n"
        "Yearly: $80\n\n"
        "VIP Benefits:\n"
        "✅ AI Buy/Sell Signals\n"
        "✅ Market Scanner\n"
        "✅ Early Coin Alerts\n"
        "✅ Platypus Rewards\n\n"
        "Contact Admin:\n"
        "@YourTelegramUsername"
    )

@bot.message_handler(commands=["help"])
def help_cmd(msg):
    bot.reply_to(
        msg,
        "🤖 LEVEL 4 AI BOT\n\n"
        "/price btc - Live price\n"
        "/signal btc - VIP signal\n"
        "/scan - VIP scanner\n"
        "/mine - Mine Plats\n"
        "/balance - Check Plats\n"
        "/leaderboard - Top miners\n"
        "/subscribe - VIP plans\n"
        "/help - Show commands"
    )

@bot.message_handler(commands=["mine"])
def mine(msg):

    user = str(msg.from_user.id)

    reward = random.randint(5,25)

    add_plats(user, reward)

balance = get_balance(user)

bot.reply_to(
    msg,
    f"🦆 Platypus mined!\n\n"
    f"+{reward} PLATS\n\n"
    f"Balance: {balance} PLATS"
)

@bot.message_handler(commands=["balance"])
def balance(msg):

    user=str(msg.from_user.id)

    bal = get_balance(user)

    bot.reply_to(
        msg,
        f"💰 Your Balance\n\n"
        f"{bal} PLATS"
    )

@bot.message_handler(commands=["leaderboard"])
def leaderboard(msg):

    top=sorted(
        plats.items(),
        key=lambda x:x[1],
        reverse=True
    )[:10]

    text="🏆 TOP PLATYPUS MINERS\n\n"

    for i,(uid,bal) in enumerate(top,1):
        text+=f"{i}. {bal} PLATS\n"

    bot.reply_to(msg,text)

@bot.message_handler(commands=["daily"])
def daily(msg):

    user=str(msg.from_user.id)

    reward=100

    if user not in plats:
        plats[user]=0

    add_plats(user, reward)

    bot.reply_to(
        msg,
        f"🎁 Daily Reward\n\n"
        f"+100 PLATS\n"
        f"Balance: {plats[user]}"
    )
# ================= FALLBACK =================

@bot.message_handler(func=lambda m: True)
def unknown(msg):
    bot.reply_to(
        msg,
        "❓ Unknown command.\n\n"
        "Use:\n"
        "/price btc\n"
        "/signal btc\n"
        "/scan\n"
        "/ping\n"
        "/test"
    )

@bot.message_handler(commands=["debug"])
def debug(msg):
    bot.reply_to(msg, "✅ Debug command works")
    
# ================= BOT LOOP =================

def run_bot():
    while True:
        try:
            print("Polling started...")

            bot.infinity_polling(
                skip_pending=True,
                timeout=30,
                long_polling_timeout=30,
                allowed_updates=["message"]
            )

        except Exception as e:
            print("POLLING CRASH:", repr(e))

            if "409" in str(e):
                print("⚠️ Another instance is using this token")

            time.sleep(5)

# ================= START =================

if __name__ == "__main__":
    print("Starting application...")

    try:
        bot.delete_webhook(drop_pending_updates=True)
        bot.remove_webhook()

        me = bot.get_me()
        print(f"Connected as @{me.username}")
        bot.send_message(7988782705, "✅ Bot restarted successfully")

    except Exception as e:
        print("Startup error:", repr(e))

    Thread(target=run_bot, daemon=True).start()

    print("Bot thread started")

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
)
