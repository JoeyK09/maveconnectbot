from telebot import types
from datetime import datetime, timedelta

from vip_keyboards import (
    vip_menu,
    vip_plans_keyboard,
    payment_keyboard
)

from vip_config import (
    VIP_PLANS,
    VIP_WALLETS,
    ADMIN_ID
)

from database import (
    get_vip_info,
    activate_vip,
    save_vip_payment,
    is_vip
)


def notify_admin(bot, user, plan, payment, reference):

    markup = types.InlineKeyboardMarkup()

    markup.row(
        types.InlineKeyboardButton(
            "✅ Approve",
            callback_data=f"approvevip_{user}"
        ),
        types.InlineKeyboardButton(
            "❌ Reject",
            callback_data=f"rejectvip_{user}"
        )
    )

    bot.send_message(
        ADMIN_ID,
        f"""
👑 VIP Payment

👤 User: {user}

💎 Plan: {VIP_PLANS[plan]["name"]}

💰 Amount: KSh {VIP_PLANS[plan]["price"]}

💳 Method: {payment}

🧾 Reference:
{reference}
""",
        reply_markup=markup
    )


def register_vip_handlers(bot):

    selected_plan = {}

    mpesa_waiting = {}

    mpesa_code_waiting = {}

    crypto_waiting = {}

    @bot.message_handler(func=lambda m: m.text == "👑 VIP Membership")
    def vip_dashboard(message):

        info = get_vip_info(str(message.from_user.id))

        if info:
            vip, plan, start, expiry = info
        else:
            vip = False
            plan = "Free"
            expiry = None

        if vip:

            text = f"""
👑 *MaveConnect VIP Dashboard*

🟢 Status: ACTIVE

💎 Plan: {plan}

📅 Expires:
{expiry}
"""

        else:

            text = """
👑 *MaveConnect VIP Dashboard*

⚪ Status: FREE MEMBER

Upgrade today to unlock premium rewards.
"""

        bot.send_message(
            message.chat.id,
            text,
            parse_mode="Markdown",
            reply_markup=vip_menu()
        )


    @bot.message_handler(func=lambda m: m.text == "📋 View Plans")
    def view_plans(message):

        bot.send_message(
            message.chat.id,
            """
👑 Choose your VIP Plan
""",
            reply_markup=vip_plans_keyboard()
        )
