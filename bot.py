import telebot
import random
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import os

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)
scheduler = BackgroundScheduler()
user_chat_id = None
reminder_job = None

# Милые фразы для случайных сообщений
sweet_messages = [
    "💖 Не забудь, ты у меня самый ответственный!",
    "🐾 Таблеточка ждёт тебя!",
    "☀️ Горжусь тобой, что заботишься о себе!",
    "🧸 Люблю тебя, не забудь принять лекарство~",
    "🌼 Твоя забота о себе делает мой день лучше!"
]

def send_reminder():
    if user_chat_id:
        bot.send_message(
            user_chat_id,
            "💊 Пора принять таблетку!\n\nНажми «Принял 💚» если уже выпил, или «Отложить на час 🕒» если позже 💕",
            reply_markup=reminder_keyboard()
        )

def send_random_sweet_message():
    if user_chat_id:
        msg = random.choice(sweet_messages)
        bot.send_message(user_chat_id, msg)

def reminder_keyboard():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("💚 Принял", callback_data="taken"),
        telebot.types.InlineKeyboardButton("🕒 Отложить на час", callback_data="delay")
    )
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    global user_chat_id
    user_chat_id = message.chat.id
    bot.send_message(message.chat.id, "Привет, солнце ☀️ Я буду напоминать тебе о таблетках каждые 30 минут с 8 утра 💊")
    schedule_daily_reminders()

def schedule_daily_reminders():
    global reminder_job
    scheduler.remove_all_jobs()

    now = datetime.now()
    start_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
    if now > start_time:
        start_time = start_time + timedelta(days=1)

    reminder_job = scheduler.add_job(send_reminder, 'interval', minutes=30, start_date=start_time)

    for _ in range(3):
        random_hour = random.randint(9, 22)
        random_minute = random.randint(0, 59)
        scheduler.add_job(send_random_sweet_message, 'cron', hour=random_hour, minute=random_minute)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "taken":
        bot.answer_callback_query(call.id, "Молодец! 🌸 Напоминания вернутся завтра 💖")
        schedule_daily_reminders()
    elif call.data == "delay":
        bot.answer_callback_query(call.id, "Окей, напомню через час 💕")
        scheduler.add_job(send_reminder, 'date', run_date=datetime.now() + timedelta(hours=1))

scheduler.start()
bot.polling(none_stop=True)
