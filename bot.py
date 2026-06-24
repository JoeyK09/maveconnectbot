import os
import time
import requests
from flask import Flask
from threading import Thread
import telebot

# ================= BOT =================

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise Exception("BOT_TOKEN not found")

bot = telebot.TeleBot(TOKEN, threaded=True)
print("Telegram bot initialized")

app = Flask(__name__)

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

# ================= PRICE ENGINE =================

def get_price(coin):
    coin = coin.lower().strip()

    if coin not in COINS:
        return None

    now = time.time()

    # Cache
    if coin in price_cache:
        cached_price, ts = price_cache[coin]

        if now - ts < CACHE_TIME:
            return cached_price

    coin_id = COINS[coin]

    # CoinGecko
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={
                "ids": coin_id,
                "vs_currencies": "usd"
            },
            timeout=5
        )

        if r.status_code == 200:
            data = r.json()

            price = data.get(coin_id, {}).get("usd")

            if price:
                price = float(price)
                price_cache[coin] = (price, now)
                return price

    except Exception as e:
        print("CoinGecko error:", e)

    # Binance fallback
    try:
        symbol = coin.upper() + "USDT"

        r = requests.get(
            "https://api.binance.com/api/v3/ticker/price",
            params={"symbol": symbol},
            timeout=5
        )

        if r.status_code == 200:
            price = float(r.json()["price"])
            price_cache[coin] = (price, now)
            return price

    except Exception as e:
        print("Binance error:", e)

    return None


def safe_get_price(coin):
    for _ in range(2):
        try:
            price = get_price(coin)

            if price is not None:
                return price

        except Exception as e:
            print("Retry error:", e)

        time.sleep(0.5)

    return None

# ================= FLASK =================

@app.route("/")
def home():
    return "LEVEL 4 AI TRADING BOT 🚀"

# ================= COMMANDS =================

@bot.message_handler(commands=["start"])
def start(msg):
    bot.reply_to(
        msg,
        "🚀 LEVEL 4 AI TRADING BOT\n\n"
        "📢 Free Group:\n"
        "https://t.me/UltimateAvian\n\n"
        "💎 VIP Group:\n"
        "https://t.me/UltimateAve\n\n"
        "Commands:\n"
        "/price btc\n"
        "/signal btc\n"
        "/ping\n"
        "/test"
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
                "❌ Coin not found or price service temporarily unavailable."
            )

    except Exception as e:
        print("Price command error:", e)
        bot.reply_to(msg, "⚠️ Error getting price")

@bot.message_handler(commands=["signal"])
def signal_cmd(msg):
    try:
        parts = msg.text.split()

        if len(parts) < 2:
            bot.reply_to(msg, "Usage: /signal btc")
            return

        coin = parts[1].lower().strip()

        price = safe_get_price(coin)

        if price is None:
            bot.reply_to(
                msg,
                "❌ Coin not found or price service temporarily unavailable."
            )
            return

        bot.reply_to(
            msg,
            f"🤖 {coin.upper()} SIGNAL\n\n"
            f"⚪ HOLD\n"
            f"💰 Price: ${price:,.4f}"
        )

    except Exception as e:
        print("Signal command error:", e)
        bot.reply_to(msg, "⚠️ Error generating signal")

@bot.message_handler(func=lambda m: True)
def unknown(msg):
    bot.reply_to(
        msg,
        "Commands:\n"
        "Use:\n"
        "/price btc\n"
        "/signal btc\n"
        "/ping\n"
        "/scan\n"
        "/test"
    )

@bot.message_handler(commands=["scan"])
def scan(msg):
    try:
        output = "📊 LEVEL 4 MARKET SCAN\n\n"

        coins_to_scan = ["btc", "eth", "bnb", "sol", "xrp"]

        for coin in coins_to_scan:
            price = safe_get_price(coin)

            if price is not None:
                output += f"✅ {coin.upper()} - ${price:,.2f}\n"
            else:
                output += f"❌ {coin.upper()} - Price unavailable\n"

        bot.send_message(msg.chat.id, output)

    except Exception as e:
        print("Scan error:", e)
        bot.reply_to(msg, "⚠️ Scan failed")
    
# ================= BOT LOOP =================

def run_bot():
    while True:
        try:
            print("Bot polling started...")

            bot.infinity_polling(
                skip_pending=True,
                timeout=30,
                long_polling_timeout=30,
                allowed_updates=["message"]
            )

        except Exception as e:
            print("Polling error:", e)
            time.sleep(5)

# ================= START =================

if __name__ == "__main__":
    print("Starting application...")

    try:
        bot.remove_webhook()
        bot.delete_webhook(drop_pending_updates=True)
        print("Webhook removed and updates cleared")
    except Exception as e:
        print("Webhook error:", e)

    Thread(target=run_bot, daemon=True).start()

    print("Bot thread started")

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
            )
