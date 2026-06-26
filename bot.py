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
    remove_plats,
    get_profile,
    update_mine,
    update_daily,
    add_win,
    leaderboard
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
    "🐶 DOGE":"doge",
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
    "💎 GRT":"grt"

    "🐶 SHIB":"shib",
    "🐸 PEPE":"pepe",
    "🐕 FLOKI":"floki",
    "🦴 BONK":"bonk",
    "🐶 WIF":"wif",
    "🍞 BRETT":"brett",

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

# ================= COINPAPRIKA IDS =================

COINPAPRIKA_IDS = {

    # Top Coins
    "btc": "btc-bitcoin",
    "eth": "eth-ethereum",
    "bnb": "bnb-binance-coin",
    "sol": "sol-solana",
    "xrp": "xrp-xrp",
    "ada": "ada-cardano",
    "doge": "doge-dogecoin",
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

# ================= PRICE ENGINE =================

def get_price(coin):
    coin = coin.lower().strip()

    if coin not in COINPAPRIKA_IDS:
        return None

    now = time.time()

    if coin in price_cache:
        price, timestamp = price_cache[coin]
        if now - timestamp < CACHE_TIME:
            return price

    try:
        r = requests.get(
            f"https://api.coinpaprika.com/v1/tickers/{COINPAPRIKA_IDS[coin]}",
            timeout=10
        )

        if r.status_code == 200:
            data = r.json()
            price = float(data["quotes"]["USD"]["price"])
            price_cache[coin] = (price, now)
            return price

    except Exception as e:
        print("CoinPaprika error:", e)

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

# =================MAIN MENU ================

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
    
# ================= TOP COINS ================

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
    
# ================= COMMANDS =================

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

    price = safe_get_price(coin)

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

@bot.message_handler(func=lambda m: m.text=="🏦 DeFi")
def defi(msg):

    text = (
        "🏦 Top DeFi Coins\n\n"
        "💰 UNI\n"
        "💰 AAVE\n"
        "💰 MKR\n"
        "💰 CRV\n"
        "💰 COMP\n"
        "💰 SUSHI\n"
        "💰 LDO\n"
        "💰 PENDLE"
    )

    bot.reply_to(msg, text)

@bot.message_handler(func=lambda m: m.text=="⚡ Layer 1")
def layer1(msg):

    text = (
        "⚡ Layer 1 Coins\n\n"
        "BTC\n"
        "ETH\n"
        "SOL\n"
        "BNB\n"
        "ADA\n"
        "AVAX\n"
        "SUI\n"
        "APT\n"
        "ATOM"
    )

    bot.reply_to(msg, text)

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

@bot.message_handler(func=lambda m: m.text=="🔎 Coin Search")
def coin_search(msg):

    bot.reply_to(
        msg,
        "🔎 Send:\n\n/price BTC\n\nor\n\n/signal ETH"
    )

@bot.message_handler(func=lambda m: m.text=="⭐ Favorites")
def favorites(msg):

    bot.reply_to(
        msg,
        "⭐ Favorites feature coming soon."
    )

@bot.message_handler(func=lambda m: m.text == "🐸 Meme Coins")
def meme_coins(msg):

    bot.send_message(
        msg.chat.id,
        "🐸 Meme Coins",
        reply_markup=memecoins_menu()
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
