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

Select one of the plans below.
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
            "🥉 Basic • KSh299": ("basic", 299),
            "🥈 Premium • KSh799": ("premium", 799),
            "🥇 Elite • KSh2499": ("elite", 2499)
        }

        plan, price = plans[message.text]

        selected_plan[message.from_user.id] = {
            "plan": plan,
            "price": price
        }

        bot.send_message(
            message.chat.id,
            f"""
👑 {plan.title()} VIP

💰 Price: KSh {price}

Choose your preferred payment method.
""",
            reply_markup=payment_keyboard()
        )
        
        # ================= PAYMENT METHOD =================

    @bot.message_handler(func=lambda m: m.text in [
        "🇰🇪 M-Pesa",
        "💵 USDT (TRC20)",
        "💵 USDT (BEP20)",
        "₿ Bitcoin",
        "♦ Ethereum"
    ])
    def payment_method(message):

        user = message.from_user.id

        if user not in selected_plan:

            bot.send_message(
                message.chat.id,
                "❌ Please choose a VIP plan first."
            )
            return

        plan = selected_plan[user]["plan"]
        price = selected_plan[user]["price"]

        # ---------- MPESA ----------

        if message.text == "🇰🇪 M-Pesa":

            mpesa_waiting[user] = True

            bot.send_message(
                message.chat.id,
                f"""
🇰🇪 *M-Pesa Payment*

👑 Plan: *{plan.title()}*
💰 Amount: *KSh {price}*

Send the payment.

Then send your M-Pesa phone number.

Example:

254712345678
""",
                parse_mode="Markdown"
            )

            return

        # ---------- CRYPTO ----------

        wallets = {
            "💵 USDT (TRC20)": VIP_WALLETS["trc20"],
            "💵 USDT (BEP20)": VIP_WALLETS["bep20"],
            "₿ Bitcoin": VIP_WALLETS["btc"],
            "♦ Ethereum": VIP_WALLETS["eth"]
        }

        crypto_waiting[user] = {
            "payment": message.text
        }

        bot.send_message(
            message.chat.id,
            f"""
💳 *{message.text}*

👑 Plan: *{plan.title()}*
💰 Amount: *KSh {price}*

Send payment to:

`{wallets[message.text]}`

After paying, send the TXID (Transaction Hash).
""",
            parse_mode="Markdown"
        )

    # ================= MPESA PHONE =================

    @bot.message_handler(func=lambda m: m.from_user.id in mpesa_waiting)
    def receive_mpesa_phone(message):

        user = message.from_user.id

        mpesa_waiting.pop(user)

        mpesa_code_waiting[user] = message.text

        bot.send_message(
            message.chat.id,
            """
✅ Phone number received.

Now send your M-Pesa Confirmation Code.

Example:

SGL8K2M9PQ
"""
        )

    # ================= MPESA CODE =================

    @bot.message_handler(func=lambda m: m.from_user.id in mpesa_code_waiting)
    def receive_mpesa_code(message):

        user = message.from_user.id

        phone = mpesa_code_waiting.pop(user)

        plan = selected_plan[user]["plan"]

        save_vip_payment(
            str(user),
            plan,
            "M-Pesa",
            message.text
        )

        notify_admin(
            bot,
            user,
            plan,
            "M-Pesa",
            f"{phone}\n{message.text}"
        )

        bot.send_message(
            message.chat.id,
            """
✅ Payment submitted.

Please wait for admin approval.
"""
        )

    # ================= CRYPTO TXID =================

    @bot.message_handler(func=lambda m: m.from_user.id in crypto_waiting)
    def receive_crypto_txid(message):

        user = message.from_user.id

        payment = crypto_waiting[user]["payment"]

        crypto_waiting.pop(user)

        plan = selected_plan[user]["plan"]

        save_vip_payment(
            str(user),
            plan,
            payment,
            message.text
        )

        notify_admin(
            bot,
            user,
            plan,
            payment,
            message.text
        )

        bot.send_message(
            message.chat.id,
            """
✅ Transaction submitted.

Your payment will be verified shortly.
"""
        )

    # ================= ADMIN APPROVE =================

    @bot.callback_query_handler(func=lambda c: c.data.startswith("approvevip_"))
    def approve(call):

        user = call.data.split("_")[1]

        activate_vip(user)

        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=None
        )

        bot.answer_callback_query(
            call.id,
            "VIP Activated."
        )

        bot.send_message(
            int(user),
            """
🎉 Congratulations!

Your VIP membership has been approved.

Welcome to MaveConnect VIP 👑
"""
        )

    # ================= ADMIN REJECT =================

    @bot.callback_query_handler(func=lambda c: c.data.startswith("rejectvip_"))
    def reject(call):

        user = call.data.split("_")[1]

        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=None
        )

        bot.answer_callback_query(
            call.id,
            "Payment rejected."
        )

        bot.send_message(
            int(user),
            """
❌ Your VIP payment was rejected.

Please contact support if you believe this is an error.
"""
        )
