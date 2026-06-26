import random
import os
import time
import requests
from flask import Flask
from threading import Thread
from database import (
    conn,
    cursor,
    get_balance,
    add_plats,
    get_profile,
    update_mine,
    update_daily
)
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

price_cache = {}
CACHE_TIME = 30
vip_users = set()

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
        f"/price btc,eth,sol,xrp,bnb\n"
        f"/signal btc,etg,sol,xrp,bnb\n"
        f"/scan\n"
        f"/mine\n"
        f"/balance\n"
        f"/leaderboard\n"
        f"/daily\n"
        f"/subscribe\n"
        f"/help\n"
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
        "@Kab3ra"
    )

@bot.message_handler(commands=["help"])
def help_cmd(msg):

    bot.reply_to(
        msg,
        "🤖 LEVEL 4 AI BOT\n\n"
        "📈 Trading\n"
        "/price btc\n"
        "/signal btc\n"
        "/scan\n\n"
        "🦆 Platypus Game\n"
        "/mine\n"
        "/daily\n"
        "/balance\n"
        "/profile\n"
        "/leaderboard\n\n"
        "💎 VIP\n"
        "/subscribe\n"
        "/help"
    )

@bot.message_handler(commands=["mine"])
def mine(msg):

    user = str(msg.from_user.id)

    balance, xp, level, last_daily, last_mine, wins = get_profile(user)

    now = int(time.time())

    cooldown = 1800

    if now - last_mine < cooldown:

        left = cooldown - (now-last_mine)

        mins = left // 60
        secs = left % 60

        bot.reply_to(
            msg,
            f"⛏ Mine cooling down.\n\n"
            f"Try again in {mins}m {secs}s"
        )

        return

    reward = random.randint(10,30)

    xp += 5

    balance += reward

    if xp >= 100:
        xp = 0
        level += 1
        balance += 50

        levelup = (
            f"\n\n🎉 LEVEL UP!\n"
            f"You reached Level {level}\n"
            f"+50 Bonus PLATS"
        )
    else:
        levelup = ""

    update_mine(
        user,
        balance,
        xp,
        level,
        now
    )

    bot.reply_to(
        msg,
        f"🦆 Mining Complete!\n\n"
        f"+{reward} PLATS\n"
        f"+5 XP\n\n"
        f"💰 Balance: {balance}\n"
        f"⭐ XP: {xp}/100\n"
        f"🏅 Level: {level}"
        f"{levelup}"
    )

@bot.message_handler(commands=["leaderboard"])
def leaderboard(msg):

    cursor.execute(
        "SELECT user_id, balance FROM plats ORDER BY balance DESC LIMIT 10"
    )

    top = cursor.fetchall()

    text = "🏆 TOP PLATYPUS MINERS\n\n"

    for i, (uid, bal) in enumerate(top, 1):
        text += f"{i}. User {uid} - {bal} PLATS\n"

    bot.reply_to(msg, text)
    
@bot.message_handler(commands=["daily"])
def daily(msg):

    user = str(msg.from_user.id)

    balance, xp, level, last_daily, last_mine, wins = get_profile(user)

    now = int(time.time())

    cooldown = 86400

    if now-last_daily < cooldown:

        left = cooldown-(now-last_daily)

        hrs = left//3600
        mins = (left%3600)//60

        bot.reply_to(
            msg,
            f"🎁 Daily already claimed.\n\n"
            f"Come back in {hrs}h {mins}m"
        )

        return

    reward = 100

    balance += reward

    update_daily(
        user,
        balance,
        now
    )

    bot.reply_to(
        msg,
        f"🎁 Daily Reward\n\n"
        f"+100 PLATS\n\n"
        f"Balance: {balance}"
    )

@bot.message_handler(commands=["profile"])
def profile(msg):

    user = str(msg.from_user.id)

    balance, xp, level, last_daily, last_mine, wins = get_profile(user)

    bot.reply_to(
        msg,
        f"👤 {msg.from_user.first_name}\n\n"
        f"🏅 Level: {level}\n"
        f"⭐ XP: {xp}/100\n\n"
        f"💰 Balance: {balance} PLATS\n"
        f"🏆 Wins: {wins}"
    )
    
# ================= FALLBACK =================

@bot.message_handler(func=lambda m: True)
def unknown(msg):
    bot.reply_to(
        msg,
        "❓ Unknown command.\n\n"
        "Use one of these commands:\n\n"
        "/price btc\n"
        "/signal btc\n"
        "/scan\n"
        "/mine\n"
        "/balance\n"
        "/leaderboard\n"
        "/daily\n"
        "/subscribe\n"
        "/help\n"
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
