import random
import os
import time
import requests
from datetime import datetime, timedelta
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from flask import Flask
from threading import Thread
from database import (
    conn,
    cursor,
    get_balance,
    add_plats,
    remove_plats,
    get_profile,
    update_mine,
    update_daily,
    add_win,
    leaderboard,
    add_favorite,
    get_favorites,
    add_alert,
    get_alerts,
    delete_alert
)
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
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

PRICE_BUTTONS = {

    "₿ BTC":"btc",
    "Ξ ETH":"eth",
    "🟡 BNB":"bnb",
    "☀️ SOL":"sol",
    "💧 XRP":"xrp",
    "🔵 ADA":"ada",
    
    "🔷 DOT":"dot",
    "⚡ LTC":"ltc",
    "🔺 TRX":"trx",
    "🏔 AVAX":"avax",
    "🔗 LINK":"link",

    "🧠 FET":"fet",
    "⚡ TAO":"tao",
    "🤖 ICP":"icp",
    "🔷 RENDER":"render",
    "🛰 AKT":"akt",
    "💎 GRT":"grt",

    "🐕 DOGE": "doge",
    "🐶 SHIB": "shib",
    "🐸 PEPE": "pepe",
    "🐕 FLOKI": "floki",
    "🦴 BONK": "bonk",
    "🐶 WIF": "wif",
    "🍞 BRETT": "brett",
    # ================= DEFI =================

    "🦄 UNI": "uni",
    "👻 AAVE": "aave",
    "🏦 MKR": "mkr",
    "📈 CRV": "crv",
    "🥞 CAKE": "cake",
    "🍣 SUSHI": "sushi",
    "🔀 1INCH": "1inch",
    "💧 LDO": "ldo",

    # ================= LAYER 1 =================

    "🌌 ATOM": "atom",
    "🌐 NEAR": "near",
    "🚀 APT": "apt",
    "💧 SUI": "sui",
    "💎 TON": "ton",
    "⚫ HBAR": "hbar",
    "⚡ KAS": "kas",
    "🦅 EGLD": "egld",
    "🔷 ALGO": "algo",
    "✔️ VET": "vet",

    # ================= RWA =================

    "💎 ONDO": "ondo",
    "🕉 OM": "om",
    "⏳ PENDLE": "pendle",
    
}

DASHBOARD_BUTTONS = [
    "🏦 DeFi",
    "⚡ Layer 1",
    "💎 RWA",
    "🎮 Games",
    "🔎 Coin Search",
    "⭐ Favorites",
    "🏠 Home"
]

# ================= CACHE =================

price_cache = {}
CACHE_TIME = 30
vip_users = set()
search_users = set()
current_coin = {}
alert_users = set()
waiting_alert = {}
user_last_coin = {}

# ================= COINPAPRIKA IDS =================

COINPAPRIKA_IDS = {

    # Top Coins
    "btc": "btc-bitcoin",
    "eth": "eth-ethereum",
    "bnb": "bnb-binance-coin",
    "sol": "sol-solana",
    "xrp": "xrp-xrp",
    "ada": "ada-cardano",
    "trx": "trx-tron",
    "avax": "avax-avalanche",
    "dot": "dot-polkadot",
    "link": "link-chainlink",
    "ltc": "ltc-litecoin",
    "bch": "bch-bitcoin-cash",
    "etc": "etc-ethereum-classic",
    "xlm": "xlm-stellar",
    "atom": "atom-cosmos",
    "near": "near-near-protocol",
    "algo": "algo-algorand",
    "vet": "vet-vechain",
    "fil": "fil-filecoin",
    "icp": "icp-internet-computer",
    "apt": "apt-aptos",
    "sui": "sui-sui",
    "ton": "ton-toncoin",
    "hbar": "hbar-hedera",
    "kas": "kas-kaspa",
    "cro": "cro-cronos",
    "qnt": "qnt-quant",
    "egld": "egld-multiversx",
    "xtz": "xtz-tezos",

    # DeFi
    "uni": "uni-uniswap",
    "aave": "aave-aave",
    "comp": "comp-compound",
    "crv": "crv-curve-dao-token",
    "mkr": "mkr-maker",
    "snx": "snx-synthetix",
    "cake": "cake-pancakeswap",
    "sushi": "sushi-sushiswap",
    "1inch": "1inch-1inch",
    "ldo": "ldo-lido-dao",

    # AI
    "fet": "fet-artificial-superintelligence-alliance",
    "tao": "tao-bittensor",
    "grt": "grt-the-graph",
    "render": "render-render",
    "akt": "akt-akash-network",
    "oas": "oas-oasys",

    # Meme
    "doge": "doge-dogecoin",
    "shib": "shib-shiba-inu",
    "pepe": "pepe-pepe",
    "floki": "floki-floki",
    "bonk": "bonk-bonk",
    "wif": "wif-dogwifcoin",
    "brett": "brett-brett",

    # Layer 2
    "arb": "arb-arbitrum",
    "op": "op-optimism",
    "imx": "imx-immutable-x",
    "zk": "zk-zksync",
    "strk": "strk-starknet",

    # Gaming
    "sand": "sand-the-sandbox",
    "mana": "mana-decentraland",
    "axs": "axs-axie-infinity",
    "gala": "gala-gala",
    "enj": "enj-enjin-coin",

    # RWA
    "ondo": "ondo-ondo-finance",
    "pendle": "pendle-pendle",
    "om": "om-mantra",

    # Privacy
    "xmr": "xmr-monero",
    "zec": "zec-zcash",

    # Storage
    "ar": "ar-arweave",
    "storj": "storj-storj",
    "sc": "sc-siacoin",

    # Oracle
    "band": "band-band-protocol",
    "api3": "api3-api3",

    # Exchange
    "okb": "okb-okb",
    "leo": "leo-unus-sed-leo",
    "bgb": "bgb-bitget-token",

    # Stablecoins
    "usdt": "usdt-tether",
    "usdc": "usdc-usd-coin",
    "dai": "dai-dai"
}

def get_coin_id(symbol):
    if not symbol:
        return None
    return COINPAPRIKA_IDS.get(symbol.lower().strip())

def get_coin_data(symbol):
    coin_id = get_coin_id(symbol)

    if not coin_id:
        return None

    try:
        url = f"https://api.coinpaprika.com/v1/tickers/{coin_id}"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None

        data = response.json()
        usd = data["quotes"]["USD"]

        return {
            "id": coin_id,
            "symbol": data["symbol"],
            "name": data["name"],
            "rank": data["rank"],
            "price": usd["price"],
            "change24": usd["percent_change_24h"],
            "market_cap": usd["market_cap"],
            "volume": usd["volume_24h"]
        }

    except Exception as e:
        print(f"CoinPaprika Error: {e}")
        return None
        
def safe_get_price(symbol):
    data = get_coin_data(symbol)

    if data:
        return data["price"]

    return None

def scan_coin(symbol):
    print(f"[SCAN] {symbol}")

    data = get_coin_data(symbol)

    if not data:
        print("[SCAN] get_coin_data failed")
        return None

    print("[SCAN] get_coin_data OK")

    history = get_history(symbol)

    if history is None:
        print("[SCAN] history is None")
    elif history.empty:
        print("[SCAN] history is empty")
    else:
        print(f"[SCAN] history rows: {len(history)}")

    analysis = ai_analysis(symbol)

    if not analysis:
        print("[SCAN] ai_analysis failed")
        return None

    print("[SCAN] ai_analysis OK")

    return {
        "coin": data["name"],
        "symbol": data["symbol"],
        "price": data["price"],
        "change24": data["change24"],
        "rank": data["rank"],
        "market_cap": data["market_cap"],
        "volume": data["volume"],
        "rsi": "N/A",
        "signal": analysis["signal"],
        "strength": analysis["strength"],
        "trend": analysis["trend"],
        "support": analysis["support"],
        "resistance": analysis["resistance"]
    }

def get_price(symbol):
    return safe_get_price(symbol)

    now = time.time()

    # cache
    if coin in price_cache:
        price, timestamp = price_cache[coin]
        if now - timestamp < CACHE_TIME:
            return price

    # resolve coin ID
    coin_id = resolve_coin(coin)

    print(f"[COIN INPUT] {symbol} → {coin_id}")
    
    if not coin_id:
        print(f"[COIN NOT FOUND] {coin}")
        return None

    try:
        url = f"https://api.coinpaprika.com/v1/tickers/{coin_id}"
        r = requests.get(url, timeout=10)

        if r.status_code != 200:
            print(f"[API ERROR] {coin} -> {r.status_code}")
            return None

        data = r.json()
        price = float(data["quotes"]["USD"]["price"])

        price_cache[coin] = (price, now)

        return price

    except Exception as e:
        print("[ERROR]", repr(e))
        return None
        
# ================== SIGNAL ENGINE =================

def get_signal(coin):

    price =get_price(coin)

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

# ================== AI ANALYSIS ==============

def ai_analysis(symbol):
    price = safe_get_price(symbol)

    if price is None:
        return {
            "signal": "UNKNOWN",
            "strength": 0,
            "trend": "Unknown",
            "support": 0,
            "resistance": 0
        }

    data = get_coin_data(symbol)
    change = data["change24"]

    if change > 5:
        signal = "🟢 BUY"
        trend = "Bullish"
        strength = 85
    elif change < -5:
        signal = "🔴 SELL"
        trend = "Bearish"
        strength = 80
    else:
        signal = "⚪ HOLD"
        trend = "Sideways"
        strength = 65

    return {
        "signal": signal,
        "strength": strength,
        "trend": trend,
        "support": round(price * 0.97, 4),
        "resistance": round(price * 1.03, 4)
    }
    
# ================= CRYPTO NEWS =================

def get_crypto_news(coin):

    try:
        url = f"https://min-api.cryptocompare.com/data/v2/news/?categories={coin.upper()}"

        r = requests.get(url, timeout=10)

        if r.status_code != 200:
            return None

        data = r.json()["Data"][:5]

        return data

    except Exception as e:
        print("News error:", e)
        return None

def calculate_rsi(df):

    rsi = RSIIndicator(df["close"]).rsi()

    return float(rsi.iloc[-1])

def calculate_trend(df):

    ema20 = EMAIndicator(df["close"], window=20).ema_indicator()

    ema50 = EMAIndicator(df["close"], window=50).ema_indicator()

    if ema20.iloc[-1] > ema50.iloc[-1]:
        return "Bullish"

    return "Bearish"
    
# =================== HISTORY ================

def get_history(symbol, days=60):
    coin_id = get_coin_id(symbol)

    if not coin_id:
        return None

    print(history.columns)
    
    start = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")

    try:
        url = (
            f"https://api.coinpaprika.com/v1/coins/"
            f"{coin_id}/ohlcv/historical?start={start}"
        )

        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None

        df = pd.DataFrame(response.json())

        if df.empty:
            return None

        df["time_open"] = pd.to_datetime(df["time_open"])
        df.set_index("time_open", inplace=True)

        return df

    except Exception as e:
        print(f"History Error: {e}")
        return None
    
# ================= FLASK =================

@app.route("/")
def home():
    return "LEVEL 4 AI TRADING BOT 🚀"

# ==================MAIN MENU ================

def main_menu():

    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row(
        KeyboardButton("📈 Trading"),
        KeyboardButton("⛏️ Mine")
    )

    markup.row(
        KeyboardButton("💳 Wallet"),
        KeyboardButton("💎 VIP")
    )

    markup.row(
        KeyboardButton("👥 Refer & Earn"),
        KeyboardButton("🎁 Daily")
    )

    markup.row(
        KeyboardButton("👤 Account"),
        KeyboardButton("🏆 Leaderboard")
    )

    markup.row(
        KeyboardButton("🎮 Games"),
        KeyboardButton("⚙️ Settings")
    )

    return markup

from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def trading_menu():

    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row(
        KeyboardButton("🟢 Top Coins"),
        KeyboardButton("🤖 AI Coins")
    )

    markup.row(
        KeyboardButton("🐸 Meme Coins"),
        KeyboardButton("🏦 DeFi")
    )

    markup.row(
        KeyboardButton("⚡ Layer 1"),
        KeyboardButton("🔍 Search Coin")
    )

    markup.row(
        KeyboardButton("🏠 Home")
    )

    return markup

def ai_menu():

    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row(
        KeyboardButton("🧠 FET"),
        KeyboardButton("⚡ TAO"),
        KeyboardButton("🤖 ICP")
    )

    markup.row(
        KeyboardButton("🔷 RENDER"),
        KeyboardButton("🛰 AKT"),
        KeyboardButton("💎 GRT")
    )

    markup.row(
        KeyboardButton("🏠 Home")
    )

    return markup


def dashboard_menu():

    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row(
        KeyboardButton("🏦 DeFi"),
        KeyboardButton("⚡ Layer 1")
    )

    markup.row(
        KeyboardButton("💎 RWA"),
        KeyboardButton("🎮 Games")
    )

    markup.row(
        KeyboardButton("🔎 Coin Search"),
        KeyboardButton("⭐ Favorites")
    )

    markup.row(
        KeyboardButton("🏠 Home")
    )

    return markup

def coin_actions():

    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row(
        KeyboardButton("📊 Chart"),
        KeyboardButton("📰 News")
    )

    markup.row(
        KeyboardButton("⭐ Favorite"),
        KeyboardButton("🔔 Set Alert")
    )

    markup.row(
        KeyboardButton("🏠 Home")
    )

    markup.row(
        KeyboardButton("🤖 AI Analysis"),
        KeyboardButton("📊 Chart")
    )

    markup.row(
        KeyboardButton("📰 News"),
        KeyboardButton("⭐ Favorite") 
    )

    markup.row(
        KeyboardButton("🔔 Set Alert"),
        KeyboardButton("🏠 Home")
    )

    markup.row(
    KeyboardButton("🤖 AI Analysis")
    )

    return markup
    
# ================= MEME COINS ================
def memecoins_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row(
        KeyboardButton("🐕 DOGE"),
        KeyboardButton("🐶 SHIB"),
        KeyboardButton("🐸 PEPE")
    )

    markup.row(
        KeyboardButton("🐕 FLOKI"),
        KeyboardButton("🦴 BONK"),
        KeyboardButton("🐶 WIF")
    )

    markup.row(
        KeyboardButton("🍞 BRETT")
    )

    markup.row(
        KeyboardButton("🏠 Home")
    )

    return markup

#=============== DEFI MENU ================
def defi_menu():

    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row(
        KeyboardButton("🦄 UNI"),
        KeyboardButton("👻 AAVE"),
        KeyboardButton("🏦 MKR")
    )

    markup.row(
        KeyboardButton("📈 CRV"),
        KeyboardButton("🥞 CAKE"),
        KeyboardButton("🍣 SUSHI")
    )

    markup.row(
        KeyboardButton("🔀 1INCH"),
        KeyboardButton("💧 LDO")
    )

    markup.row(
        KeyboardButton("🏠 Home")
    )

    return markup
    
# ================= TOP COINS ===============

def topcoins_menu():

    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row(
        KeyboardButton("₿ BTC"),
        KeyboardButton("Ξ ETH"),
        KeyboardButton("🟡 BNB")
    )

    markup.row(
        KeyboardButton("☀️ SOL"),
        KeyboardButton("💧 XRP"),
        KeyboardButton("🔵 ADA")
    )

    markup.row(
        KeyboardButton("🐶 DOGE"),
        KeyboardButton("🔷 DOT"),
        KeyboardButton("⚡ LTC")
    )

    markup.row(
        KeyboardButton("🔺 TRX"),
        KeyboardButton("🏔 AVAX"),
        KeyboardButton("🔗 LINK")
    )

    markup.row(
        KeyboardButton("🏠 Home")
    )

    return markup

# ================ LAYER 1 =============

def layer1_menu():

    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row(
        KeyboardButton("🌌 ATOM"),
        KeyboardButton("🌐 NEAR"),
        KeyboardButton("🚀 APT")
    )

    markup.row(
        KeyboardButton("💧 SUI"),
        KeyboardButton("💎 TON"),
        KeyboardButton("⚫ HBAR")
    )

    markup.row(
        KeyboardButton("⚡ KAS"),
        KeyboardButton("🦅 EGLD"),
        KeyboardButton("🔷 ALGO")
    )

    markup.row(
        KeyboardButton("✔️ VET")
    )

    markup.row(
        KeyboardButton("🏠 Home")
    )

    return markup

# ================= DEFI ===============

def rwa_menu():

    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row(
        KeyboardButton("💎 ONDO"),
        KeyboardButton("🕉 OM"),
        KeyboardButton("⏳ PENDLE")
    )

    markup.row(
        KeyboardButton("🏠 Home")
    )

    return markup
    
# ================= COMMANDS ================

@bot.message_handler(commands=["start"])
def start(msg):

    bot.send_message(
        msg.chat.id,
        f"👋 Welcome to MaveConnect!\n\n"
        f"🚀 LEVEL 4 AI TRADING BOT\n\n"
        f"📢 Free Group:\n{FREE_GROUP}\n\n"
        f"💎 VIP Group:\n{VIP_GROUP}\n\n"
        f"Use the menu below 👇",
        reply_markup=main_menu()
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
        
        #Save the last coin viewed
        user_last_coin[msg.from_user.id] = coin
        
        price =get_price(coin)

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
        "💎 LEVEL 4 VIP\n\n"
        "Choose a plan:\n\n"
        "⭐ 250 Stars - 1 Month VIP\n"
        "⭐ 650 Stars - 3 Months VIP\n"
        "⭐ 2,000 Stars - Lifetime VIP\n\n"
        "Use /buyvip to purchase."
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
            f"⛏️ Mine cooling down.\n\n"
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
def leaderboard_cmd(msg):

    top = leaderboard()

    text = "🏆 TOP PLATYPUS MINERS\n\n"

    if not top:
        text += "No miners yet."
    else:
        for i, (uid, bal) in enumerate(top, 1):
            text += f"{i}. {bal} PLATS\n"

    bot.reply_to(msg, text)

@bot.message_handler(commands=["balance"])
def balance(msg):

    user = str(msg.from_user.id)

    balance = get_balance(user)

    bot.reply_to(
        msg,
        f"💰 Balance\n\n"
        f"{balance} PLATS"
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

@bot.message_handler(commands=["buyvip"])
def buyvip(msg):
    bot.reply_to(
        msg,
        "⭐ Telegram Stars payment is coming soon.\n\n"
        "For now contact @Kab3ra to activate VIP."
    )

@bot.message_handler(commands=["activatevip"])
def activate(msg):

    if msg.from_user.id != ADMIN_ID:
        return

    parts = msg.text.split()

    if len(parts) != 2:
        bot.reply_to(msg, "Usage:\n/activatevip USER_ID")
        return

    user_id = parts[1]

    vip_users.add(int(user_id))

    bot.reply_to(msg, "✅ VIP activated.")

@bot.message_handler(func=lambda m: m.text=="👤 Account")
def account_btn(msg):
    profile(msg)


@bot.message_handler(func=lambda m: m.text=="💳 Wallet")
def wallet_btn(msg):
    balance(msg)


@bot.message_handler(func=lambda m: m.text=="💎 VIP")
def vip_btn(msg):
    subscribe(msg)


@bot.message_handler(func=lambda m: m.text=="🏆 Leaderboard")
def leaderboard_btn(msg):
    leaderboard_cmd(msg)


@bot.message_handler(func=lambda m: m.text=="🎁 Daily")
def daily_btn(msg):
    daily(msg)


@bot.message_handler(func=lambda m: m.text=="⛏ Mine")
def mine_btn(msg):
    mine(msg)


@bot.message_handler(func=lambda m: m.text == "📈 Trading")
def trading(msg):

    bot.send_message(
        msg.chat.id,
        "📈 Trading Center\n\nChoose a category.",
        reply_markup=trading_menu()
    )


@bot.message_handler(func=lambda m: m.text=="👥 Refer & Earn")
def refer_btn(msg):
    bot.reply_to(
        msg,
        "👥 Referral System\n\n"
        "🚧 Coming Soon!"
    )


@bot.message_handler(func=lambda m: m.text=="🎮 Games")
def games_btn(msg):
    bot.reply_to(
        msg,
        "🎮 Games\n\n"
        "🎲 Dice\n"
        "🪙 Coin Flip\n"
        "🎰 Slots\n\n"
        "Coming in the next update!"
    )


@bot.message_handler(func=lambda m: m.text=="⚙️ Settings")
def settings_btn(msg):
    bot.reply_to(
        msg,
        "⚙️ Settings\n\n"
        "Coming Soon!"
    )


@bot.message_handler(func=lambda m: m.text == "🏠 Home")
def home_btn(msg):

    bot.send_message(
        msg.chat.id,
        "🏠 Main Menu",
        reply_markup=main_menu()
    )


@bot.message_handler(func=lambda m: m.text == "💲 Price")
def price_menu(msg):

    bot.reply_to(
        msg,
        "Send a command like:\n\n"
        "/price btc\n"
        "/price eth\n"
        "/price sol"
    )


@bot.message_handler(func=lambda m: m.text == "🤖 Signal")
def signal_menu(msg):

    bot.reply_to(
        msg,
        "Send a command like:\n\n"
        "/signal btc\n"
        "/signal eth"
    )


@bot.message_handler(func=lambda m: m.text == "📊 Scan")
def scan_menu(msg):
    scan(msg)


@bot.message_handler(func=lambda m: m.text == "🟢 Top Coins")
def topcoins(msg):

    bot.send_message(
        msg.chat.id,
        "💰 Top Coins",
        reply_markup=topcoins_menu()
    )

@bot.message_handler(func=lambda m: m.text in PRICE_BUTTONS)
def coin_price(msg):

    coin = PRICE_BUTTONS[msg.text]

    price =get_price(coin)

    if price is None:
        bot.reply_to(msg, "❌ Price unavailable.")
        return

    bot.reply_to(
        msg,
        f"💰 {coin.upper()}\n\n"
        f"Price: ${price:,.4f}"
    )

@bot.message_handler(func=lambda m: m.text == "🏠 Home")
def home_button(msg):

    bot.send_message(
        msg.chat.id,
        "🏠 Main Menu",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda m: m.text == "🤖 AI Coins")
def ai_coins(msg):

    bot.send_message(
        msg.chat.id,
        "🤖 AI Coins",
        reply_markup=ai_menu()
    )

@bot.message_handler(func=lambda m: m.text=="📊 Market Dashboard")
def dashboard(msg):

    bot.reply_to(
        msg,
        "📊 Market Dashboard\n\nChoose a category:",
        reply_markup=dashboard_menu()
    )

@bot.message_handler(func=lambda m: m.text == "🏦 DeFi")
def defi(msg):
    bot.send_message(
        msg.chat.id,
        "🏦 Top DeFi Coins",
        reply_markup=defi_menu()
    )
    
@bot.message_handler(func=lambda m: m.text=="💎 RWA")
def rwa(msg):

    text = (
        "💎 Real World Asset Coins\n\n"
        "ONDO\n"
        "LINK\n"
        "POLYX\n"
        "CFG\n"
        "OM\n"
        "MPL"
    )

    bot.reply_to(msg, text)

@bot.message_handler(func=lambda m: m.text=="🎮 Games")
def games(msg):

    text = (
        "🎮 Gaming Coins\n\n"
        "IMX\n"
        "GALA\n"
        "BEAM\n"
        "RON\n"
        "PIXEL\n"
        "SAND\n"
        "MANA\n"
        "AXS"
    )

    bot.reply_to(msg, text)
    
@bot.message_handler(func=lambda m: m.text == "🔎 Coin Search")
def coin_search(msg):

    search_users.add(msg.from_user.id)

    bot.reply_to(
        msg,
        "🔎 Send a coin symbol.\n\n"
        "Examples:\n"
        "BTC\n"
        "ETH\n"
        "SOL\n"
        "SUI\n"
        "ONDO"
    )

@bot.message_handler(func=lambda m: m.text == "⭐ Favorite")
def favorite(msg):

    coin = current_coin.get(msg.from_user.id)

    if not coin:
        bot.reply_to(msg, "❌ Open a coin first.")
        return

    add_favorite(str(msg.from_user.id), coin)

    bot.reply_to(
        msg,
        f"⭐ {coin.upper()} saved to Favorites!"
    )

@bot.message_handler(func=lambda m: m.text == "⭐ Favorites")
def favorites(msg):

    favs = get_favorites(str(msg.from_user.id))

    if not favs:
        bot.reply_to(msg, "⭐ You don't have any favorite coins yet.")
        return

    text = "⭐ Your Favorite Coins\n\n"

    for coin in favs:
        price = get_price(coin)

        if price:
            text += f"• {coin.upper()} — ${price:,.4f}\n"
        else:
            text += f"• {coin.upper()}\n"

    bot.reply_to(msg, text)
    
@bot.message_handler(func=lambda m: m.text == "🐸 Meme Coins")
def meme_coins(msg):

    bot.send_message(
        msg.chat.id,
        "🐸 Meme Coins",
        reply_markup=memecoins_menu()
    )

@bot.message_handler(func=lambda m: m.text == "⚡ Layer 1")
def layer1(msg):

    bot.send_message(
        msg.chat.id,
        "⚡ Top Layer 1 Coins",
        reply_markup=layer1_menu()
    )

@bot.message_handler(func=lambda m: m.text == "💎 RWA")
def rwa(msg):

    bot.send_message(
        msg.chat.id,
        "💎 Real World Asset (RWA) Coins",
        reply_markup=rwa_menu()
    )

@bot.message_handler(func=lambda m: m.text == "🔍 Search Coin")
def search_coin(msg):

    search_users.add(msg.from_user.id)

    bot.send_message(
        msg.chat.id,
        "🔎 Send a coin symbol.\n\nExamples:\nBTC\nETH\nDOGE\nSUI\nONDO"
    )


@bot.message_handler(func=lambda m: m.from_user.id in search_users)
def search_coin_result(msg):

    search_users.discard(msg.from_user.id)

    coin = msg.text.lower().strip()

    user_last_coin[msg.from_user.id] = coin
    current_coin[msg.from_user.id] = coin

    scan = scan_coin(coin)

    if scan is None:
        bot.reply_to(msg, "❌ Coin not found.")
        return

    if isinstance(scan["rsi"], (int, float)):
        rsi_status = (
           "Oversold 🟢" if scan["rsi"] < 30 else
           "Overbought 🔴" if scan["rsi"] > 70 else
           "Neutral ⚪"
       )
    else:
       rsi_status = "Unavailable"
    
    current_coin[msg.from_user.id] = coin
    
    bot.reply_to(
    msg,
    f"🪙 {scan['coin']} ({scan['symbol']})\n\n"
    f"💰 Price: ${scan['price']:,.6f}\n"
    f"📈 24H: {scan['change24']:.2f}%\n"
    f"🏆 Rank: #{scan['rank']}\n"
    f"💎 Market Cap: ${scan['market_cap']:,.0f}\n"
    f"📊 Volume: ${scan['volume']:,.0f}\n\n"
    f"🤖 AI Analysis\n"
    f"📊 RSI (14): {scan['rsi']} ({rsi_status})\n"
    f"Signal: {scan['signal']}\n"
    f"Strength: {scan['strength']}/100\n"
    f"Trend: {scan['trend']}\n"
    f"Support: ${scan['support']:,.4f}\n"
    f"Resistance: ${scan['resistance']:,.4f}"
    )

#@bot.message_handler(func=lambda m: m.from_user.id in search_users)
#def handle_coin_input(msg):

   # coin = msg.text.upper().strip()

    #user_last_coin[msg.from_user.id] = coin
    #search_users.discard(msg.from_user.id)

   # bot.reply_to(
      #  msg,
       # f"✅ Coin selected: {coin}\n\n"
       # f"You can now use:\n📊 Chart\n📰 News\n🔔 Set Alert"
  #  )
    
@bot.message_handler(func=lambda m: m.text == "📊 Chart")
def chart(msg):

    coin = user_last_coin.get(msg.from_user.id)

    if not coin:
        bot.reply_to(msg, "❌ Open a coin first.")
        return

    bot.reply_to(
        msg,
        f"📈 {coin.upper()} Chart\n\n"
        f"https://www.tradingview.com/symbols/{coin.upper()}USDT/"
    )

@bot.message_handler(func=lambda m: m.text == "📰 News")
def news(msg):

    coin = user_last_coin.get(msg.from_user.id)

    if not coin:
        bot.reply_to(msg, "Open a coin first.")
        return

    articles = get_crypto_news(coin)

    if not articles:
        bot.reply_to(msg, "No news available.")
        return

    text = f"📰 Latest {coin.upper()} News\n\n"

    for article in articles:
        text += (
            f"• {article['title']}\n"
            f"{article['url']}\n\n"
        )

    bot.send_message(msg.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "⭐ Favorite")
def favorite(msg):
    bot.reply_to(
        msg,
        "⭐ Added to Favorites!"
    )

@bot.message_handler(func=lambda m: m.text == "🔔 Set Alert")
def set_alert(msg):
    coin = user_last_coin.get(msg.from_user.id)

    if not coin:
        bot.reply_to(msg, "Search a coin first.")
        return

    waiting_alert[msg.from_user.id] = coin

    bot.reply_to(
        msg,
        f"Enter the target price for {coin.upper()}.\n\nExample:\n120000"
    )


@bot.message_handler(func=lambda m: m.from_user.id in waiting_alert)
def save_alert(msg):
    coin = waiting_alert.pop(msg.from_user.id)

    try:
        target = float(msg.text)

        add_alert(
            str(msg.from_user.id),
            coin,
            target
        )

        bot.reply_to(
            msg,
            f"✅ Alert set!\n{coin.upper()} → ${target:,.2f}"
        )

    except:
        bot.reply_to(msg, "Invalid price.")

@bot.message_handler(func=lambda m: m.text == "📊 Chart")
def chart(msg):

    coin = user_last_coin.get(msg.from_user.id)

    if not coin:
        bot.reply_to(msg, "❌ View a coin first.")
        return

    symbol = coin.upper()

    bot.reply_to(
        msg,
        f"📈 Live {symbol} Chart\n\n"
        f"https://www.tradingview.com/chart/?symbol=BINANCE:{symbol}USDT"
)

@bot.message_handler(func=lambda m: m.text == "📰 News")
def news(msg):

    coin = current_coin.get(msg.from_user.id)

    if not coin:
        bot.reply_to(msg, "❌ Open a coin first.")
        return

    bot.reply_to(
        msg,
        f"📰 Fetching the latest news for {coin.upper()}..."
    )

@bot.message_handler(func=lambda m: m.text == "⭐ Favorite")
def favorite(msg):

    coin = current_coin.get(msg.from_user.id)

    if not coin:
        bot.reply_to(msg, "❌ Open a coin first.")
        return

    bot.reply_to(
        msg,
        f"⭐ {coin.upper()} added to your favorites."
    )
    
@bot.message_handler(func=lambda m: m.text == "🔔 Set Alert")
def alert(msg):

    coin = current_coin.get(msg.from_user.id)

    if not coin:
        bot.reply_to(msg, "❌ Open a coin first.")
        return

    bot.reply_to(
        msg,
        f"🔔 Enter the target price for {coin.upper()}."
    )

@bot.message_handler(func=lambda m: m.text == "🔔 Set Alert")
def alert(msg):

    coin = current_coin.get(msg.from_user.id)

    if not coin:
        bot.reply_to(msg, "❌ Open a coin first.")
        return

    alert_users.add(msg.from_user.id)

    bot.reply_to(
        msg,
        f"Enter the target price for {coin.upper()}.\n\nExample:\n120000"
    )

@bot.message_handler(func=lambda m: m.from_user.id in alert_users)
def save_alert(msg):

    alert_users.discard(msg.from_user.id)

    coin = current_coin[msg.from_user.id]

    try:
        target = float(msg.text)

    except ValueError:
        bot.reply_to(msg, "❌ Invalid price.")
        return

    add_alert(
        str(msg.from_user.id),
        coin,
        target
    )

    bot.reply_to(
        msg,
        f"✅ Alert created!\n\n{coin.upper()} → ${target:,.2f}"
    )

@bot.message_handler(func=lambda m: m.text == "🤖 AI Analysis")
def ai_analysis_handler(msg):

    coin = user_last_coin.get(msg.from_user.id)

    if not coin:
        bot.reply_to(msg, "Open a coin first.")
        return

    result = get_ai_analysis(coin)

    if result is None:
        bot.reply_to(msg, "Unable to analyze this coin.")
        return

    bot.reply_to(
        msg,
        f"🤖 AI Analysis for {coin.upper()}\n\n"
        f"📈 Trend: {result['trend']}\n"
        f"🎯 Signal: {result['signal']}\n"
        f"🛡 Risk: {result['risk']}\n"
        f"💪 Confidence: {result['confidence']}%\n\n"
        f"🟢 Support: ${result['support']:,.4f}\n"
        f"🔴 Resistance: ${result['resistance']:,.4f}"
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

def alert_checker():

    while True:

        for user, coin, target in get_alerts():

            price = get_price(coin)

            if price and price >= target:

                bot.send_message(
                  int(user),
                  f"🚨 {coin.upper()} has reached ${price:,.2f}!"
                )

                delete_alert(user, coin, target)

        time.sleep(60)   # Check every 60 seconds
        
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
        bot.send_message(6384391560, "✅ Bot restarted successfully")

    except Exception as e:
        print("Startup error:", repr(e))

    # Start alert checker
    Thread(target=alert_checker, daemon=True).start()

    # Start Telegram bot
    Thread(target=run_bot, daemon=True).start()

    print("Bot thread started")

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
