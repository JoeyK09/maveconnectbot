import random
import time
from database import get_balance, add_plats, remove_plats

from telebot.types import ReplyKeyboardMarkup, KeyboardButton

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
            # ==========================
# COIN FLIP
# ==========================

@bot.message_handler(func=lambda m: m.text == "🪙 Coin Flip")
def start_coinflip(message):

    bot.send_message(
        message.chat.id,
        "🪙 Coin Flip\n\n"
        "Enter the amount of Plats you want to bet."
    )

    bot.register_next_step_handler(message, process_coinflip_bet)


# ==========================
# DICE ROLL
# ==========================

@bot.message_handler(func=lambda m: m.text == "🎲 Dice Roll")
def dice_roll(message):
    bot.send_message(
        message.chat.id,
        "🎲 Dice Roll\n\n"
        "This game is under construction.\n"
        "Coming soon!"
    )


# ==========================
# SLOT MACHINE
# ==========================

@bot.message_handler(func=lambda m: m.text == "🎰 Slot Machine")
def slot_machine(message):
    bot.send_message(
        message.chat.id,
        "🎰 Slot Machine\n\n"
        "This game is under construction.\n"
        "Coming soon!"
    )


# ==========================
# LUCKY NUMBER
# ==========================

@bot.message_handler(func=lambda m: m.text == "🎯 Lucky Number")
def lucky_number(message):
    bot.send_message(
        message.chat.id,
        "🎯 Lucky Number\n\n"
        "This game is under construction.\n"
        "Coming soon!"
    )


# ==========================
# LEADERBOARD
# ==========================

@bot.message_handler(func=lambda m: m.text == "🏆 Leaderboard")
def leaderboard(message):
    bot.send_message(
        message.chat.id,
        "🏆 Leaderboard\n\n"
        "No games have been played yet."
    )


# ==========================
# GAME HISTORY
# ==========================

@bot.message_handler(func=lambda m: m.text == "📜 Game History")
def history(message):
    bot.send_message(
        message.chat.id,
        "📜 Game History\n\n"
        "No history available."
    )


# ==========================
# DAILY BONUS
# ==========================

@bot.message_handler(func=lambda m: m.text == "🎁 Daily Bonus")
def daily_bonus(message):
    bot.send_message(
        message.chat.id,
        "🎁 Daily Bonus\n\n"
        "Coming soon!"
    )
)
