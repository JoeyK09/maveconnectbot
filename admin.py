from telebot import types
from vip_config import ADMIN_ID
from admin_keyboards import admin_menu

def register_admin_handlers(bot):

    @bot.message_handler(commands=["admin"])
    def admin_panel(message):

        if message.from_user.id != ADMIN_ID:
            bot.reply_to(
                message,
                "❌ You are not authorized."
            )
            return

        bot.send_message(
            message.chat.id,
            """
👑 *MaveConnect Admin Panel*

Choose an option below.
""",
            parse_mode="Markdown",
            reply_markup=admin_menu()
        )

# ================= ADMIN PANEL =================

@bot.message_handler(commands=["admin"])
def admin_panel(message):

    if message.from_user.id != ADMIN_ID:

        bot.reply_to(
            message,
            "❌ You are not authorized to use this command."
        )
        return

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row("💳 Pending Payments")
    markup.row("👥 VIP Members", "📊 Statistics")
    markup.row("📢 Broadcast", "⚙ VIP Settings")
    markup.row("🔙 Back")

    bot.send_message(
        message.chat.id,
        """
👑 *MaveConnect Admin Panel*

Welcome, Admin.

Choose an option below.
""",
        parse_mode="Markdown",
        reply_markup=markup
    )


# ================= PENDING PAYMENTS =================

@bot.message_handler(func=lambda m: m.text == "💳 Pending Payments")
def pending_payments(message):

    if message.from_user.id != ADMIN_ID:
        return

    bot.send_message(
        message.chat.id,
        "💳 Pending payments will appear here."
    )


# ================= VIP MEMBERS =================

@bot.message_handler(func=lambda m: m.text == "👥 VIP Members")
def vip_members(message):

    if message.from_user.id != ADMIN_ID:
        return

    bot.send_message(
        message.chat.id,
        "👥 VIP members list coming soon."
    )


# ================= STATISTICS =================

@bot.message_handler(func=lambda m: m.text == "📊 Statistics")
def admin_statistics(message):

    if message.from_user.id != ADMIN_ID:
        return

    bot.send_message(
        message.chat.id,
        "📊 Statistics dashboard coming soon."
    )


# ================= BROADCAST =================

@bot.message_handler(func=lambda m: m.text == "📢 Broadcast")
def broadcast(message):

    if message.from_user.id != ADMIN_ID:
        return

    bot.send_message(
        message.chat.id,
        "📢 Broadcast feature coming soon."
    )


# ================= VIP SETTINGS =================

@bot.message_handler(func=lambda m: m.text == "⚙ VIP Settings")
def vip_settings(message):

    if message.from_user.id != ADMIN_ID:
        return

    bot.send_message(
        message.chat.id,
        "⚙ VIP settings coming soon."
    )


# ================= BACK =================

@bot.message_handler(func=lambda m: m.text == "🔙 Back")
def admin_back(message):

    if message.from_user.id != ADMIN_ID:
        return

    bot.send_message(
        message.chat.id,
        "🏠 Returned to the main menu."
    )
