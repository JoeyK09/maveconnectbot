from telebot import types


def vip_menu():

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

    kb.row("📋 View Plans")
    kb.row("📅 My Subscription", "🎁 VIP Benefits")
    kb.row("👥 VIP Channel", "📜 Payment History")
    kb.row("🔄 Renew VIP")
    kb.row("🔙 Back")

    return kb


def vip_plans_keyboard():

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row("🥉 Basic • KSh299")
    markup.row("🥈 Premium • KSh799")
    markup.row("🥇 Elite • KSh2499")

    markup.row("🔙 Back")

    return markup


def payment_keyboard():

    kb = types.InlineKeyboardMarkup()

    kb.add(
        types.InlineKeyboardButton(
            "🇰🇪 M-Pesa",
            callback_data="pay_mpesa"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "💵 USDT TRC20",
            callback_data="pay_trc20"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "💵 USDT BEP20",
            callback_data="pay_bep20"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "₿ Bitcoin",
            callback_data="pay_btc"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "♦ Ethereum",
            callback_data="pay_eth"
        )
    )

    return kb
