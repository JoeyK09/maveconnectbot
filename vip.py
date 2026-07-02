from telebot import types
from datetime import datetime, timedelta

from vip_keyboards import *
from vip_config import *

from database import (
    get_vip_info,
    activate_vip,
    save_vip_payment,
    is_vip
)

def register_vip_handlers(bot):

    selected_plan = {}
    mpesa_waiting = {}
    mpesa_code_waiting = {}
    crypto_waiting = {}

    @bot.message_handler(func=lambda m: crypto_waiting.get(m.from_user.id))
def receive_crypto_txid(message):

    user = message.from_user.id
    txid = message.text.strip()

    method = crypto_waiting.pop(user)

    plan = selected_plan[user]

    save_vip_payment(
        str(user),
        plan,
        VIP_PLANS[plan]["price"],
        method.upper(),
        txid
    )

    notify_admin(
        bot,
        user,
        plan,
        method.upper(),
        txid
    )

    bot.send_message(
        message.chat.id,
        "✅ Payment submitted successfully.\n\nYour VIP will be activated after verification."
    )

    @bot.message_handler(func=lambda m: mpesa_waiting.get(m.from_user.id))
def receive_mpesa_number(message):

    user = message.from_user.id

    phone = message.text.strip()

    mpesa_waiting.pop(user)

    mpesa_code_waiting[user] = phone

    plan = selected_plan[user]

    bot.send_message(
        message.chat.id,
        f"""
🇰🇪 M-Pesa Payment

Send:

KSh {VIP_PLANS[plan]["price"]}

To:

0142047838

After payment send your M-Pesa confirmation code.
"""
    )

    @bot.message_handler(func=lambda m: mpesa_code_waiting.get(m.from_user.id))
def receive_mpesa_code(message):

    user = message.from_user.id

    code = message.text.strip()

    phone = mpesa_code_waiting.pop(user)

    plan = selected_plan[user]

    save_vip_payment(
        str(user),
        plan,
        VIP_PLANS[plan]["price"],
        "MPESA",
        code
    )

    notify_admin(
        bot,
        user,
        plan,
        phone,
        code
    )

    bot.send_message(
        message.chat.id,
        "✅ Payment submitted.\n\nWaiting for verification."
    )

    @bot.callback_query_handler(func=lambda c: c.data.startswith("approvevip_"))
def approve(call):

    user = int(call.data.split("_")[1])

    plan = selected_plan[user]

    expiry = datetime.now() + timedelta(days=VIP_PLANS[plan]["days"])

    activate_vip(
        str(user),
        plan,
        expiry
    )

    bot.send_message(
        user,
        f"""
🎉 Congratulations!

Your {VIP_PLANS[plan]["name"]} subscription is now active.

Enjoy your premium benefits!
"""
    )

    bot.edit_message_text(
        "✅ VIP Activated",
        call.message.chat.id,
        call.message.message_id
    )

    @bot.callback_query_handler(func=lambda c: c.data.startswith("approvevip_"))
def approve(call):

    user = int(call.data.split("_")[1])

    plan = selected_plan[user]

    expiry = datetime.now() + timedelta(days=VIP_PLANS[plan]["days"])

    activate_vip(
        str(user),
        plan,
        expiry
    )

    bot.send_message(
        user,
        f"""
🎉 Congratulations!

Your {VIP_PLANS[plan]["name"]} subscription is now active.

Enjoy your premium benefits!
"""
    )

    bot.edit_message_text(
        "✅ VIP Activated",
        call.message.chat.id,
        call.message.message_id
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

💰 Amount:
KSh {VIP_PLANS[plan]["price"]}

💳 Method:
{payment}

🧾 Reference:
{reference}
""",
        reply_markup=markup
    )


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
👑 *MaveConnect VIP*

🟢 Status: ACTIVE

💎 Plan: {plan}

📅 Expires:
{expiry}
"""

        else:

            text = """
👑 *MaveConnect VIP*

⚪ Status: FREE

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
👑 Choose a VIP Plan

Select one below.
""",
            reply_markup=vip_plans_keyboard()
        )

@bot.callback_query_handler(func=lambda c: c.data.startswith("vip_"))
    def choose_plan(call):

        plan = call.data.replace("vip_", "")

        selected_plan[call.from_user.id] = plan

        bot.edit_message_text(
            f"""
✅ {VIP_PLANS[plan]['name']}

Price:
KSh {VIP_PLANS[plan]['price']}

Choose your payment method.
""",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=payment_keyboard()
        )

@bot.callback_query_handler(func=lambda c: c.data.startswith("pay_"))
    def payment(call):

        user = call.from_user.id

        if user not in selected_plan:

            bot.answer_callback_query(
                call.id,
                "Select a VIP plan first."
            )

            return

        method = call.data.replace("pay_", "")

        if method == "mpesa":

            mpesa_waiting[user] = True

            bot.send_message(
                call.message.chat.id,
                "📱 Enter your M-Pesa phone number."
            )

            return

        wallet = VIP_WALLETS[method]

        crypto_waiting[user] = method

        bot.send_message(
            call.message.chat.id,
            f"""
Send payment to:

`{wallet}`

Then send your TXID.
""",
            parse_mode="Markdown"
        )

