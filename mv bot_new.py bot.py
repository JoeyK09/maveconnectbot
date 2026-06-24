import os
import time
import requests
from flask import flask
from threading import thread
import telebot
‎
‎# ================= BOT =================
‎
‎TOKEN = os.getenv("BOT_TOKEN")
‎
‎if not TOKEN:
‎    raise Exception("BOT_TOKEN not found")
‎
‎bot = telebot.TeleBot(TOKEN, threaded=True)
‎print("Telegram bot initialized")
‎
‎app = Flask(__name__)
‎
‎# ================= GROUPS =================
‎
‎FREE_GROUP = "https://t.me/UltimateAvian"
‎VIP_GROUP = "https://t.me/UltimateAve"
‎VIP_CHANNEL = "@UltimateAve"
‎
‎# ================= COINS =================
‎
‎COINS = {
‎    "btc": "bitcoin",
‎    "eth": "ethereum",
‎    "bnb": "binancecoin",
‎    "sol": "solana",
‎    "xrp": "ripple",
‎    "ada": "cardano",
‎    "doge": "dogecoin",
‎    "matic": "matic-network",
‎    "dot": "polkadot",
‎    "ltc": "litecoin",
‎    "trx": "tron",
‎    "avax": "avalanche-2",
‎    "shib": "shiba-inu",
‎    "link": "chainlink"
‎}
‎
‎# ================= CACHE =================
‎
‎price_cache = {}
‎CACHE_TIME = 30
‎
‎# ================= PRICE ENGINE =================

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
            timeout=10
        )

        print("CoinGecko Status:", r.status_code)

        if r.status_code == 200:
            data = r.json()

            price = data.get(coin_id, {}).get("usd")

            if price is not None:
                price = float(price)
                price_cache[coin] = (price, now)
                return price

    except Exception as e:
        print("CoinGecko error:", repr(e))

    # Binance fallback
    try:
        symbol = coin.upper() + "USDT"

        r = requests.get(
            "https://api.binance.com/api/v3/ticker/price",
            params={"symbol": symbol},
            timeout=10
        )

        if r.status_code == 200:
            price = float(r.json()["price"])
            price_cache[coin] = (price, now)
            return price

    except Exception as e:
        print("Binance error:", repr(e))

    return None


def safe_get_price(coin):
    for _ in range(3):
        try:
            price = get_price(coin)

            if price is not None:
                return price

        except Exception as e:
            print("Retry error:", repr(e))

        time.sleep(1)

    return None
‎    
‎# ================= SIGNAL ENGINE =================
‎
‎def get_signal(coin):
‎    price = safe_get_price(coin)
‎
‎    if price is None:
‎        return None
‎
‎    score = int((price % 50) + 50)
‎
‎    if score >= 85:
‎        action = "🟢 STRONG BUY"
‎    elif score >= 70:
‎        action = "🟢 BUY"
‎    elif score >= 55:
‎        action = "⚪ HOLD"
‎    else:
‎        action = "🔴 SELL"
‎
‎    return {
‎        "price": price,
‎        "score": score,
‎        "action": action
‎    }
