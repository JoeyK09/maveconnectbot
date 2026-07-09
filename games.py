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
        KeyboardButton("🏆 Leaderboard"),
        KeyboardButton("📜 Game History")
    )

    markup.row(
        KeyboardButton("🎁 Daily Bonus")
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

    # ----------------------------
    # Games Menu
    # ----------------------------
    @bot.message_handler(func=lambda m: m.text == "🎮 Games")
    def open_games(message):

        bot.send_message(
            message.chat.id,
            "🎮 *Welcome to MaveConnect Games!*\n\n"
            "Play games, earn Mave Coins and climb the leaderboard.\n\n"
            "Choose a game below.",
            parse_mode="Markdown",
            reply_markup=games_menu()
        )

    # ----------------------------
    # Back Button
    # ----------------------------
    @bot.message_handler(func=lambda m: m.text == "🔙 Back")
    def back_button(message):

        game_states.pop(message.from_user.id, None)

        # Replace this with your main menu keyboard.
        bot.send_message(
            message.chat.id,
            "🏠 Main Menu.",
            reply_markup=main_menu()
            
