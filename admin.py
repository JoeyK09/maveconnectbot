from telebot import types
from vip_config import ADMIN_ID
from admin_keyboards import admin_menu


def register_admin_handlers(bot):

    @bot.message_handler(commands=["admin"])
    def admin_panel(message):

        if str(message.from_user.id) != str(ADMIN_ID):
            bot.reply_to(message, "❌ You are not authorized.")
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


    @bot.message_handler(func=lambda m: m.text == "💳 Pending Payments")
    def pending_payments(message):

        if str(message.from_user.id) != str(ADMIN_ID):
            return

        bot.send_message(
            message.chat.id,
            "💳 Pending payments will appear here."
        )


    @bot.message_handler(func=lambda m: m.text == "👥 VIP Members")
    def vip_members(message):

        if str(message.from_user.id) != str(ADMIN_ID):
            return

        bot.send_message(
            message.chat.id,
            "👥 VIP members list coming soon."
        )


    @bot.message_handler(func=lambda m: m.text == "📊 Statistics")
    def statistics(message):

        if str(message.from_user.id) != str(ADMIN_ID):
            return

        bot.send_message(
            message.chat.id,
            "📊 Statistics coming soon."
        )


    @bot.message_handler(func=lambda m: m.text == "📢 Broadcast")
    def broadcast(message):

        if str(message.from_user.id) != str(ADMIN_ID):
            return

        bot.send_message(
            message.chat.id,
            "📢 Broadcast feature coming soon."
        )


    @bot.message_handler(func=lambda m: m.text == "⚙ VIP Settings")
    def vip_settings(message):

        if str(message.from_user.id) != str(ADMIN_ID):
            return

        bot.send_message(
            message.chat.id,
            "⚙ VIP settings coming soon."
        )


    @bot.message_handler(func=lambda m: m.text == "🔙 Back")
    def back(message):

        if str(message.from_user.id) != str(ADMIN_ID):
            return

        bot.send_message(
            message.chat.id,
            "🏠 Back to main menu."
        )
