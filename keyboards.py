from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu():

    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row(
        KeyboardButton("📈 Trading"),
        KeyboardButton("⛏️ Mine")
    )

    markup.row(
        KeyboardButton("💳 Mave Wallet"),
        KeyboardButton("👑 VIP MEMBERSHIP")
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

    markup.row(
        KeyboardButton("🤝 Partners")
    )

    return markup

markup = types.InlineKeyboardMarkup()

markup.row(
    types.InlineKeyboardButton(
        "✅ Approve",
        callback_data=f"approvevip_{user_id}"
    ),
    types.InlineKeyboardButton(
        "❌ Reject",
        callback_data=f"rejectvip_{user_id}"
    )
)
