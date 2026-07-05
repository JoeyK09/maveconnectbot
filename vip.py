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

👤 User ID: {user}

💎 Plan: {VIP_PLANS[plan]["name"]}

💰 Amount: KSh {VIP_PLANS[plan]["price"]}

💳 Payment Method:
{payment}

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

    @bot.message_handler(func=lambda m: m.text == "✅ I've Paid")
    def mpesa_paid(message):

        user = message.from_user.id

        if user not in selected_plan:
            bot.send_message(
                message.chat.id,
                "❌ Please select a VIP plan first."
            )
            return

        mpesa_code_waiting[user] = True

        bot.send_message(
            message.chat.id,
            """
🧾 *Enter your M-PESA Transaction Code.*

Example:

`TIQ8ABC123`
""",
            parse_mode="Markdown"
        )


    # ================= VIP DASHBOARD =================

    @bot.message_handler(func=lambda m: m.text == "👑 VIP MEMBERSHIP")
    def vip_dashboard(message):

        info = get_vip_info(str(message.from_user.id))

        if info:
            active, plan, start, expiry = info
        else:
            active = False
            plan = "Free"
            expiry = None

        if active:

            text = f"""
👑 *MaveConnect VIP Dashboard*

🟢 Status: *ACTIVE*

💎 Plan: *{plan.title()}*

📅 Expires:
`{expiry}`

Select an option below.
"""

        else:

            text = """
👑 *MaveConnect VIP Dashboard*

⚪ Status: *FREE MEMBER*

Upgrade today and enjoy:

⛏️ 2× Mining Rewards

💰 2× Faucet Rewards

🎁 Daily VIP Bonus

⚡ Faster Withdrawals

🎉 VIP Giveaways

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
👑 *Choose Your VIP Plan*

Select one of the plans below.
""",
            parse_mode="Markdown",
            reply_markup=vip_plans_keyboard()
        )

    # ================= MY SUBSCRIPTION =================

    @bot.message_handler(func=lambda m: m.text == "📅 My Subscription")
    def my_subscription(message):

        info = get_vip_info(str(message.from_user.id))

        if not info or not info[0]:

            bot.send_message(
                message.chat.id,
                "❌ You don't have an active VIP subscription."
            )
            return

        active, plan, start, expiry = info

        bot.send_message(
            message.chat.id,
            f"""
👑 *Your VIP Subscription*

💎 Plan: *{plan.title()}*

📅 Started:
`{start}`

⏳ Expires:
`{expiry}`

🟢 Status: *Active*
""",
            parse_mode="Markdown"
        )

    # ================= PLAN SELECTION =================

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
👑 *{plan.title()} VIP*

💰 Price: *KSh {price}*

Choose your preferred payment method.
""",
            parse_mode="Markdown",
            reply_markup=payment_keyboard()
            )

    # ================= PAYMENT METHODS =================

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

            markup = types.InlineKeyboardMarkup()

            markup.add(
                types.InlineKeyboardButton(
                    "✅ I've Paid",
                    callback_data="vip_paid_mpesa"
                )
            )

            bot.send_message(
                message.chat.id,
                f"""
🇰🇪 *M-PESA Payment*

👑 Plan: *{plan.title()}*

💰 Amount: *KSh {price}*

━━━━━━━━━━━━━━

Send the payment to:

📱 *0142047838*

👤 *Joseph Gichimu*

━━━━━━━━━━━━━━

After paying, tap *I've Paid* below.

Your VIP membership will be activated after verification.
""",
                parse_mode="Markdown",
                reply_markup=markup
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

After sending the payment, reply with your TXID (Transaction Hash).
""",
            parse_mode="Markdown"
        )

    # ================= I'VE PAID =================

@bot.message_handler(func=lambda m: m.text == "✅ I've Paid")
def mpesa_paid(message):

    user = message.from_user.id

    # Ensure the user selected a plan first
    if user not in selected_plan:
        bot.send_message(
            message.chat.id,
            "❌ Please select a VIP plan first."
        )
        return

    # Wait for the transaction code
    mpesa_code_waiting[user] = True

    bot.send_message(
        message.chat.id,
        """
🧾 *Enter your M-PESA Transaction Code.*

Example:

`TIQ8ABC123`

After sending the code, your payment will be submitted for verification.
""",
        parse_mode="Markdown"
    )
    
    # ================= RECEIVE MPESA CODE =================

    @bot.message_handler(func=lambda m: m.from_user.id in mpesa_code_waiting)
    def receive_mpesa_code(message):

        user = message.from_user.id

        mpesa_code_waiting.pop(user)

        if user not in selected_plan:
            bot.send_message(
                message.chat.id,
                "❌ VIP plan not found. Please start again."
            )
            return

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
            message.text
        )

        bot.send_message(
            message.chat.id,
            """
✅ Your payment has been submitted successfully.

⏳ Please wait while an administrator verifies your payment.

You'll receive a notification once your VIP membership is activated.
"""
        )

    # ================= RECEIVE CRYPTO TXID =================

    @bot.message_handler(func=lambda m: m.from_user.id in crypto_waiting)
    def receive_crypto_txid(message):

        user = message.from_user.id

        payment = crypto_waiting[user]["payment"]

        crypto_waiting.pop(user)

        if user not in selected_plan:
            bot.send_message(
                message.chat.id,
                "❌ VIP plan not found."
            )
            return

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
✅ Transaction submitted successfully.

⏳ Your payment is awaiting verification.

You'll be notified once your VIP membership is activated.
"""
        )

    # ================= ADMIN APPROVE =================

    @bot.callback_query_handler(func=lambda c: c.data.startswith("approvevip_"))
    def approve_vip(call):

        user = call.data.split("_")[1]

        activate_vip(user)

        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None
        )

        bot.answer_callback_query(
            call.id,
            "VIP activated successfully."
        )

        bot.send_message(
            int(user),
            """
🎉 Congratulations!

Your VIP payment has been approved.

👑 Welcome to MaveConnect VIP!

Enjoy your exclusive benefits.
"""
        )

    # ================= ADMIN REJECT =================

    @bot.callback_query_handler(func=lambda c: c.data.startswith("rejectvip_"))
    def reject_vip(call):

        user = call.data.split("_")[1]

        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None
        )

        bot.answer_callback_query(
            call.id,
            "Payment rejected."
        )

        bot.send_message(
            int(user),
            """
❌ Unfortunately, your VIP payment could not be verified.

If you believe this is a mistake, please contact MaveConnect support.
"""
        )
