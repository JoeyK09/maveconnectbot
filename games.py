import random
import time

from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from database import (
    get_balance,
    add_plats,
    remove_plats,
    add_win,
    leaderboard
)

# ===============USER STATE ==============================

game_states = {}
coinflip_bets = {}
# Example:
# game_states[user_id] = {
#     "game": "coinflip",
#     "step": "bet"
# }

# ============================================
# DATABASE ADAPTER
# Replace these with your database functions.
# ============================================

def get_balance(user_id):
    """Return user's Mave Coin balance."""
    return 0


def add_balance(user_id, amount):
    """Add coins."""
    pass


def remove_balance(user_id, amount):
    """Remove coins."""
    pass


def save_game_history(user_id, game, result, amount):
    """Save game result."""
    pass


def get_game_history(user_id):
    """Return game history."""
    return []

# ============================================
# GAMES MENU
# ============================================

from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def games_menu():

    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row(
        KeyboardButton("🪙 Coin Flip"),
        KeyboardButton("🎲 Dice Roll")
    )

    markup.row(
        KeyboardButton("🎰 Slot Machine"),
        KeyboardButton("🎯 Lucky Number")
    )

    markup.row(
        KeyboardButton("🎁 Daily Bonus"),
        KeyboardButton("🎉 Jackpot")
    )

    markup.row(
        KeyboardButton("🏆 Leaderboard"),
        KeyboardButton("📜 History")
    )

    markup.row(
        KeyboardButton("🛒 Mining Shop")
    )

    markup.row(
        KeyboardButton("🔙 Back")
    )

    return markup

from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def coinflip_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    markup.row(
        KeyboardButton("🪙 Heads"),
        KeyboardButton("🪙 Tails")
    )

    markup.row(
        KeyboardButton("❌ Cancel")
    )

    return markup
# ============================================
# REGISTER ALL GAME HANDLERS
# ============================================

def register_game_handlers(bot):

    # ==========================================
    # GAMES MENU
    # ==========================================

    @bot.message_handler(func=lambda m: m.text == "🎮 Games")
    def open_games(message):

        user_id = str(message.from_user.id)

        # Create profile if it doesn't exist
        get_profile(user_id)

        balance = get_balance(user_id)

        bot.send_message(
            message.chat.id,
            f"""
🎮 <b>Welcome to MaveConnect Games!</b>

💰 <b>Your Balance:</b> <code>{balance:,}</code> Plats

━━━━━━━━━━━━━━━━━━━

🎲 <b>Available Games</b>

🪙 Coin Flip
🎲 Dice Roll
🎰 Slot Machine
🎯 Lucky Number

━━━━━━━━━━━━━━━━━━━

🏆 Win Plats
🔥 Build Win Streaks
🎁 Claim Daily Bonuses
📜 View Game History
🥇 Climb the Leaderboard

👇 <b>Select a game below.</b>
""",
            parse_mode="HTML",
            reply_markup=games_menu()
        )

    # ==========================================
    # BACK BUTTON
    # ==========================================

    @bot.message_handler(func=lambda m: m.text == "🔙 Back")
    def back_button(message):

        game_states.pop(message.from_user.id, None)

        bot.send_message(
            message.chat.id,
            "🏠 Main Menu",
            reply_markup=main_menu()
        )
