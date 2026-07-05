from telebot import types
from admin_keyboards import admin_menu
from vip_config import ADMIN_ID


def register_admin_handlers(bot):

    @bot.message_handler(commands=["admin"])
    def admin_panel(message):

        if message.from_user.id != ADMIN_ID:
            return

        bot.send_message(
            message.chat.id,
            """
🛡 *MaveConnect Admin Panel*

Welcome, Admin.

Choose an option below.
""",
            parse_mode="Markdown",
            reply_markup=admin_menu()
        )
