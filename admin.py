from telebot import types

from vip_config import ADMIN_ID

from database import approve_vip_payment, reject_vip_payment

from database import get_all_pending_vip_payments

from admin_keyboards import admin_menu

from database import (
    get_total_users,
    get_total_vip,
    get_pending_vip_payments,
    get_pending_withdrawals,
    get_all_pending_vip_payments,
    approve_vip_payment,
    reject_vip_payment
)


def register_admin_handlers(bot):

    broadcast_waiting = {}

    # ================= ADMIN PANEL =================

    @bot.message_handler(commands=["admin"])
    def admin_panel(message):

        if str(message.from_user.id) != str(ADMIN_ID):
            bot.reply_to(
                message,
                "❌ You are not authorized."
            )
            return

        bot.send_message(
            message.chat.id,
            """
👑 *MaveConnect Admin Panel*

Welcome Administrator.

Choose an option below.
""",
            parse_mode="Markdown",
            reply_markup=admin_menu()
        )

    # ================= STATISTICS =================

    @bot.message_handler(func=lambda m: m.text == "📊 Statistics")
    def statistics(message):

        if str(message.from_user.id) != str(ADMIN_ID):
            return

        try:

            users = get_total_users()
            vip = get_total_vip()
            pending = get_pending_vip_payments()
            withdrawals = get_pending_withdrawals()

            bot.send_message(
                message.chat.id,
                f"""
📊 *MaveConnect Statistics*

👥 Total Users: *{users}*

👑 Active VIP Members: *{vip}*

💳 Pending VIP Payments: *{pending}*

💰 Pending Withdrawals: *{withdrawals}*
""",
                parse_mode="Markdown"
            )

        except Exception as e:

            bot.send_message(
                message.chat.id,
                f"❌ Error loading statistics:\n\n`{e}`",
                parse_mode="Markdown"
            )

    # ================= PENDING PAYMENTS =================

    @bot.message_handler(func=lambda m: m.text == "💳 Pending Payments")
    def pending_payments(message):

        if str(message.from_user.id) != str(ADMIN_ID):
            return

        try:

            payments = get_all_pending_vip_payments()

            if not payments:

                bot.send_message(
                    message.chat.id,
                    "✅ There are no pending VIP payments."
                )
                return

            for payment in payments:

                markup = types.InlineKeyboardMarkup()

                markup.row(
                    types.InlineKeyboardButton(
                        "✅ Approve",
                        callback_data=f"approvevip_{payment['id']}"
                    ),
                    types.InlineKeyboardButton(
                        "❌ Reject",
                        callback_data=f"rejectvip_{payment['id']}"
                    )
                )

                bot.send_message(
                    message.chat.id,
                    f"""
👤 User: `{payment['user_id']}`

💎 Plan: *{payment['plan'].title()}*

💳 Method: *{payment['payment_method']}*

🧾 Reference:

`{payment['reference']}`
""",
                    parse_mode="Markdown",
                    reply_markup=markup
                )

        except Exception as e:

            bot.send_message(
                message.chat.id,
                f"❌ {e}"
                )
            # ================= APPROVE VIP =================

@bot.callback_query_handler(func=lambda call: call.data.startswith("approvevip_"))
def approve_vip_callback(call):

    if str(call.from_user.id) != str(ADMIN_ID):
        bot.answer_callback_query(call.id, "Unauthorized")
        return

    payment_id = call.data.split("_")[1]

    result = approve_vip_payment(payment_id)

    if not result:

        bot.answer_callback_query(
            call.id,
            "Approval failed."
        )

        return

    bot.answer_callback_query(
        call.id,
        "VIP Approved!"
    )

    bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.message_id,
        reply_markup=None
    )

    bot.send_message(
        result["user_id"],
        f"""🎉 Congratulations!

Your *{result["plan"].title()} VIP Membership* has been approved.

Welcome to MaveConnect VIP! 👑""",
        parse_mode="Markdown"
    )


# ================= REJECT VIP =================

@bot.callback_query_handler(func=lambda call: call.data.startswith("rejectvip_"))
def reject_vip_callback(call):

    if str(call.from_user.id) != str(ADMIN_ID):
        bot.answer_callback_query(call.id, "Unauthorized")
        return

    payment_id = call.data.split("_")[1]

    user_id = reject_vip_payment(payment_id)

    if not user_id:

        bot.answer_callback_query(
            call.id,
            "Rejection failed."
        )

        return

    bot.answer_callback_query(
        call.id,
        "Payment Rejected."
    )

    bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.message_id,
        reply_markup=None
    )

    bot.send_message(
        user_id,
        """❌ Your VIP payment has been rejected.

If you believe this is an error, please contact MaveConnect Support."""
    )
