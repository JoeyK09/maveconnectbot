from telebot import types
from datetime import datetime, timedelta
from database import get_vip_info

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

    # ================= VIP DASHBOARD =================

    @bot.message_handler(func=lambda m: m.text == "👑 VIP MEMBERSHIP")
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

🟢 Status: *ACTIVE*

💎 Plan: *{plan}*

📅 Expires:
`{expiry}`
"""

        else:

            text = """
👑 *MaveConnect VIP Dashboard*

⚪ Status: *FREE MEMBER*

Upgrade today to unlock:

⛏ 2× Mining Rewards
💰 2× Faucet Rewards
🎁 Daily VIP Bonus
⚡ Faster Withdrawals
🎉 Exclusive Giveaways

Tap *📋 View Plans* below.
"""

        bot.send_message(
            message.chat.id,
            text,
            parse_mode="Markdown",
            reply_markup=vip_menu()
        )

    # ================= VIEW PLANS =================

    @bot.message_handler(func=lambda m: m.text == "📋 View Plans")
def view_plans(message):

    bot.send_message(
        message.chat.id,
        """
👑 Choose your VIP Plan

🥉 Basic - KSh299
🥈 Premium - KSh799
🥇 Elite - KSh2499
""",
        reply_markup=vip_plans_keyboard()
    )
    
    # ================= MY SUBSCRIPTION =================

    @bot.message_handler(func=lambda m: m.text == "📅 My Subscription")
    def my_subscription(message):

        info = get_vip_info(str(message.from_user.id))

        if not info:

            bot.send_message(
                message.chat.id,
                "❌ You don't have an active VIP subscription."
            )
            return

        active, plan, start, expiry = info

        if not active:

            bot.send_message(
                message.chat.id,
                "❌ Your VIP subscription has expired."
            )
            return

        bot.send_message(
            message.chat.id,
            f"""
👑 *Your VIP Subscription*

💎 Plan: *{plan}*

📅 Started:
`{start}`

⏳ Expires:
`{expiry}`

🟢 Status: *Active*
""",
            parse_mode="Markdown"
        )

    # ================= CHOOSE PLAN =================

    @bot.message_handler(func=lambda m: m.text in [
    "🥉 Basic • KSh299",
    "🥈 Premium • KSh799",
    "🥇 Elite • KSh2499"
])
def choose_plan(message):

    plans = {
        "🥉 Basic • KSh299": ("Basic", 299),
        "🥈 Premium • KSh799": ("Premium", 799),
        "🥇 Elite • KSh2499": ("Elite", 2499)
    }

    plan, price = plans[message.text]

    selected_plan[message.from_user.id] = {
        "plan": plan,
        "price": price
    }

    bot.send_message(
        message.chat.id,
        f"""
👑 {plan} VIP

💰 Price: KSh {price}

Choose your payment method.
""",
        reply_markup=payment_keyboard()
    )
