from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from datetime import datetime
import logging

from config import BOT_TOKEN, AUTHORIZED_USERS, SCHEDULE_GENERATION_DAY, AUTO_UPDATE_INTERVAL
from database import init_db, add_user, get_shifts_by_date, get_shifts_by_bartender, get_last_generation_date, set_last_generation_date, approve_swap_request, reject_swap_request
from utils import generate_schedule, create_calendar_image
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from threading import Thread

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

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

# ---
