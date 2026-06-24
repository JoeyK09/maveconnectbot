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

# ================= GROUPS =================

FREE_GROUP = "https://t.me/UltimateAvian"
VIP_GROUP = "https://t.me/UltimateAve"
VIP_CHANNEL = "@UltimateAve"

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

        print("CoinGecko Status:", r.status_code)
        print("CoinGecko Response:", r.text)

        if r.status_code == 200:
            data = r.json()

            price = data.get(coin_id, {}).get("usd")

            if price is not None:
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
    
# ================= SIGNAL ENGINE =================

def get_signal(coin):
    price = safe_get_price(coin)

    if price is None:
        return None

    score = int((price % 50) + 50)

    if score >= 85:
        action = "🟢 STRONG BUY"
    elif score >= 70:
        action = "🟢 BUY"
    elif score >= 55:
        action = "⚪ HOLD"
    else:
        action = "🔴 SELL"

    return {
        "price": price,
        "score": score,
        "action": action
    }

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
            f"🔥 Strength: {result['score']}/100"
        )

    except Exception as e:
        print("Signal error:", repr(e))
        bot.reply_to(msg, "⚠️ Error generating signal")

@bot.message_handler(commands=["scan"])
def scan(msg):
    try:
        output = "📊 LEVEL 4 MARKET SCAN\n\n"

        for coin in COINS.keys():
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

# ================= BOT LOOP =================

def run_bot():
    while True:
        try:
            print("Polling started...")

            bot.infinity_polling(
                skip_pending=True,
                timeout=20,
                long_polling_timeout=20
            )

        except Exception as e:
            print("POLLING CRASH:", repr(e))
            time.sleep(10)
            
# ================= START =================

if __name__ == "__main__":
    print("Starting application...")

    try:
        bot.delete_webhook(drop_pending_updates=True)
        bot.remove_webhook()

        me = bot.get_me()
        print(f"Connected as @{me.username}")

    except Exception as e:
        print("Startup error:", repr(e))

    Thread(target=run_bot, daemon=True).start()

    print("Bot thread started")

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
            )
