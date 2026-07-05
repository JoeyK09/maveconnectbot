from telebot import types

def admin_menu():

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

    kb.row("👥 Users", "👑 VIP")

    kb.row("💸 Withdrawals", "💰 Finance")

    kb.row("📢 Broadcast", "📊 Statistics")

    kb.row("⚙ Settings")

    kb.row("🔙 Back")

    return kb
