from telebot import types

from vip_config import ADMIN_ID

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
            # ================= ADMIN =================

def get_all_pending_vip_payments():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id,
               user_id,
               plan,
               payment_method,
               reference
        FROM vip_payments
        WHERE status='pending'
        ORDER BY id ASC
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    payments = []

    for row in rows:
        payments.append({
            "id": row[0],
            "user_id": row[1],
            "plan": row[2],
            "payment_method": row[3],
            "reference": row[4]
        })

    return payments


def approve_vip_payment(payment_id):

    conn = get_connection()
    cur = conn.cursor()

    # Get payment details
    cur.execute("""
        SELECT user_id, plan
        FROM vip_payments
        WHERE id=%s
    """, (payment_id,))

    payment = cur.fetchone()

    if payment is None:
        cur.close()
        conn.close()
        return False

    user_id, plan = payment

    # Approve payment
    cur.execute("""
        UPDATE vip_payments
        SET status='approved'
        WHERE id=%s
    """, (payment_id,))

    # Activate VIP
    activate_vip(str(user_id))

    conn.commit()

    cur.close()
    conn.close()

    return True


def reject_vip_payment(payment_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE vip_payments
        SET status='rejected'
        WHERE id=%s
    """, (payment_id,))

    conn.commit()

    cur.close()
    conn.close()

    return True
    # ================= APPROVE VIP =================

    @bot.callback_query_handler(func=lambda c: c.data.startswith("approvevip_"))
    def approve_vip_callback(call):

        if str(call.from_user.id) != str(ADMIN_ID):
            bot.answer_callback_query(call.id, "Unauthorized")
            return

        payment_id = call.data.split("_")[1]

        if approve_vip_payment(payment_id):

            bot.edit_message_reply_markup(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=None
            )

            bot.answer_callback_query(
                call.id,
                "VIP Approved!"
            )

            bot.send_message(
                call.message.chat.id,
                "✅ VIP payment approved successfully."
            )

        else:

            bot.answer_callback_query(
                call.id,
                "Payment not found."
            )


    # ================= REJECT VIP =================

    @bot.callback_query_handler(func=lambda c: c.data.startswith("rejectvip_"))
    def reject_vip_callback(call):

        if str(call.from_user.id) != str(ADMIN_ID):
            bot.answer_callback_query(call.id, "Unauthorized")
            return

        payment_id = call.data.split("_")[1]

        reject_vip_payment(payment_id)

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
            call.message.chat.id,
            "❌ VIP payment rejected."
    )
