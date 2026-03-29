from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard():
    keyboard = [
        ["📅 Сегодня", "👤 Мои смены"],
        ["🗓 Месяц", "📷 Календарь"],
        ["🔄 Обновить месяц", "❌ Не могу выйти"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_swap_keyboard(requests):
    keyboard = []
    for req in requests:
        keyboard.append([
            InlineKeyboardButton(
                f"✅ {req['from_user']} → {req['shift_date']} {req['shift_time']}",
                callback_data=f"approve_{req['id']}"
            ),
            InlineKeyboardButton("❌", callback_data=f"reject_{req['id']}")
        ])
    return InlineKeyboardMarkup(keyboard) if keyboard else None

def get_cancel_keyboard():
    keyboard = [[InlineKeyboardButton("❌ Отмена", callback_data="cancel")]]
    return InlineKeyboardMarkup(keyboard)

