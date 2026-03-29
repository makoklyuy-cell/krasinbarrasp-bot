import os
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

from config import BOT_TOKEN, AUTHORIZED_USERS, SCHEDULE_GENERATION_DAY, AUTO_UPDATE_INTERVAL
from database import init_db, add_user, get_shifts_by_date, get_shifts_by_bartender, get_last_generation_date, set_last_generation_date, approve_swap_request, reject_swap_request
from keyboards import get_main_keyboard
from utils import generate_schedule, create_calendar_image

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from threading import Thread

# --- 🌐 KEEP ALIVE ---
app_web = Flask('')

@app_web.route('/')
def home():
    return "🍸 KrasinBar Bot is alive!"

@app_web.route('/health')
def health():
    return {"status": "ok"}, 200

def run_flask():
    app_web.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# --- ⏰ АВТО-ОБНОВЛЕНИЕ ---
def auto_generate_schedule():
    today = datetime.now()
    if today.day == SCHEDULE_GENERATION_DAY:
        last_gen = get_last_generation_date()
        if last_gen != today.strftime("%Y-%m"):
            generate_schedule()
            set_last_generation_date(today.strftime("%Y-%m"))
            print("✅ Расписание обновлено автоматически")

# --- 🤖 HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user.username
    telegram_id = update.message.from_user.id
    
    if username not in AUTHORIZED_USERS:
        return await update.message.reply_text("❌ У вас нет доступа к этому боту.")
    
    add_user(telegram_id, username, AUTHORIZED_USERS[username])
    
    if not get_last_generation_date():
        generate_schedule()
        set_last_generation_date(datetime.now().strftime("%Y-%m"))
    
    await update.message.reply_text(
        f"🍸 Привет, {AUTHORIZED_USERS[username]}!\n\nДобро пожаловать в **KrasinBar Rasp**",
        reply_markup=get_main_keyboard()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.from_user.username
    text = update.message.text
    
    if username not in AUTHORIZED_USERS:
        return
    
    worker_name = AUTHORIZED_USERS[username]
    
    if text == "📅 Сегодня":
        today = datetime.now().strftime("%d.%m")
        shifts = get_shifts_by_date(today)
        if shifts:
            msg = f"📅 **Сегодня ({today}):**\n\n"
            for shift in shifts:
                msg += f"⏰ {shift['time']} — {shift['bartender']}\n"
            await update.message.reply_text(msg)
        else:
            await update.message.reply_text("❌ На сегодня смен нет.")
    
    elif text == "👤 Мои смены":
        shifts = get_shifts_by_bartender(worker_name)
        if shifts:
            msg = f"👤 **Твои смены, {worker_name}:**\n\n"
            for shift in shifts:
                msg += f"📅 {shift['date']} ⏰ {shift['time']}\n"
            await update.message.reply_text(msg)
        else:
            await update.message.reply_text("❌ У тебя нет запланированных смен.")
    
    elif text == "🗓 Месяц":
        shifts = get_shifts_by_bartender(worker_name)
        if shifts:
            msg = f"🗓 **Все смены на месяц:**\n\n"
            for shift in shifts:
                msg += f"{shift['date']} — {shift['time']} ({shift['bartender']})\n"
            await update.message.reply_text(msg)
        else:
            await update.message.reply_text("❌ Смен нет.")
    
    elif text == "📷 Календарь":
        try:
            file_path = create_calendar_image(username)
            await update.message.reply_photo(photo=open(file_path, "rb"))
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка генерации календаря: {e}")
    
    elif text == "🔄 Обновить месяц":
        generate_schedule()
        set_last_generation_date(datetime.now().strftime("%Y-%m"))
        await update.message.reply_text("✅ Расписание обновлено!")
    
    elif text == "❌ Не могу выйти":
        await update.message.reply_text(
            "🔄 **Запрос на обмен сменой**\n\n"
            "Напиши дату и время смены в формате:\n"
            "`ДД.ММ ЧЧ:ММ`\n\n"
            "Пример: `15.03 17:00`"
        )
        context.user_data['waiting_for_swap'] = True

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("approve_"):
        request_id = int(data.split("_")[1])
        approve_swap_request(request_id)
        await query.edit_message_text("✅ Смена обменена!")
    
    elif data.startswith("reject_"):
        request_id = int(data.split("_")[1])
        reject_swap_request(request_id)
        await query.edit_message_text("❌ Запрос отклонён.")
    
    elif data == "cancel":
        await query.edit_message_text("❌ Отменено.")

# --- 🚀 ЗАПУСК ---
if __name__ == '__main__':
    print("🔧 Инициализация базы данных...")
    init_db()
    
    print("📅 Проверка расписания...")
    if not get_last_generation_date():
        generate_schedule()
        set_last_generation_date(datetime.now().strftime("%Y-%m"))
    
    print("⏰ Запуск планировщика...")
    scheduler = BackgroundScheduler()
    scheduler.add_job(auto_generate_schedule, "interval", hours=AUTO_UPDATE_INTERVAL)
    scheduler.start()
    
    print("🤖 Запуск бота...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("🌐 Запуск веб-сервера (anti-sleep)...")
    keep_alive()
    
    print("🚀 Бот запущен и готов к работе!")
    app.run_polling()

