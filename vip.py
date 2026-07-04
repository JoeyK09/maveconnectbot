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

    @bot.message_handler(func=lambda m: m.text == "👑 Vip Membership")
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
            "👑 *Choose a VIP Plan*",
            parse_mode="Markdown",
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

    @bot.callback_query_handler(func=lambda c: c.data.startswith("vip_"))
    def choose_plan(call):

        plans = {
            "vip_basic": ("🥉 Basic", 299),
            "vip_premium": ("🥈 Premium", 799),
            "vip_elite": ("🥇 Elite", 2499)
        }

        if call.data not in plans:
            bot.answer_callback_query(call.id, "Invalid VIP plan.")
            return

        plan, price = plans[call.data]

        selected_plan[call.from_user.id] = {
            "plan": plan,
            "price": price
        }

        markup = types.InlineKeyboardMarkup()

        markup.add(
            types.InlineKeyboardButton(
                "🇰🇪 M-Pesa",
                callback_data="vippay_mpesa"
            )
        )

        markup.add(
            types.InlineKeyboardButton(
                "💵 USDT (TRC20)",
                callback_data="vippay_trc20"
            )
        )

        markup.add(
            types.InlineKeyboardButton(
                "💵 USDT (BEP20)",
                callback_data="vippay_bep20"
            )
        )

        markup.add(
            types.InlineKeyboardButton(
                "₿ Bitcoin",
                callback_data="vippay_btc"
            )
        )

        markup.add(
            types.InlineKeyboardButton(
                "♦ Ethereum",
                callback_data="vippay_eth"
            )
        )

        bot.edit_message_text(
            f"""
👑 *{plan} VIP*

💰 Price: *KSh {price}*

Choose your preferred payment method.
""",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=markup
        )
      
