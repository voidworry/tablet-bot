import telebot
import random
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import os

# ------------------- настройки -------------------
TOKEN = os.getenv("TOKEN")
OWNER_CHAT_ID = os.getenv("OWNER_CHAT_ID") 

if not TOKEN:
    raise ValueError("TOKEN не найден в переменных окружения!")
if not OWNER_CHAT_ID:
    raise ValueError("OWNER_CHAT_ID не найден в переменных окружения!")

OWNER_CHAT_ID = int(OWNER_CHAT_ID)
print("token и owner_chat_id загружены успешно.")

bot = telebot.TeleBot(TOKEN)
scheduler = BackgroundScheduler()
user_chat_id = None

# ------------------- контент -------------------
sweet_messages = [
    "💖 напоминаю, я тебя люблю ❣️",
    "🐾 ты у меня самый замечательный ✨",
    "☀️ горжусь тобой, что заботишься о себе 🌸",
    "🧸 надеюсь, ты чувствуешь себя хорошо >.<",
    "🌼 твоя забота о себе делает мой день лучше 🌷",
    "💛 ты самый смелый и сильный ⭐️",
    "🌸 моё сердце радуется, когда думаю о тебе 🫶",
    "🐱 не забывай улыбаться, ты чудо ❣️",
    "✨ каждый день с тобой особенный 🌟",
    "💐 ты заслуживаешь только счастья 🍀",
    "🌞 твоя энергия делает мир ярче ☀️",
    "🫂 помни, я всегда рядом мысленно с тобой 💫",
    "💌 ты делаешь меня счастливой просто своим существованием 🐾",
    "🎀 ты — моя радость и вдохновение 🌸",
    "🥰 я горжусь тобой за каждое маленькое усилие ✨",
    "💫 ты такой уникальный, что словами не описать ❣️",
    "🌷 твоя доброта делает мир лучше 🐱",
    "💭 думаю о тебе и улыбаюсь 🌸",
    "🧡 ты наполняешь мой день теплом 🌞",
    "🐝 ты - моё счастье ⭐️",
    "🍀 желаю тебе сегодня только удачи и радости ✨",
    "🎶 ты сводишь меня с ума 🐾",
    "💎 ты - моё сокровище ❣️",
    "🌹 твоя улыбка — лучик солнца ☀️",
    "🪷 я верю в тебя, всегда и во всём 🌸"
]

memes = [
    "https://i.yapx.ru/cEGTF.jpg",
    "https://i.yapx.ru/cEGTH.jpg",
    "https://i.yapx.ru/cEGTI.jpg",
    "https://i.yapx.ru/cEGTJ.jpg",
    "https://i.yapx.ru/cEGTK.jpg",
    "https://i.yapx.ru/cEGTL.jpg",
    "https://i.yapx.ru/cEGTM.jpg",
    "https://i.yapx.ru/cEGTO.jpg",
    "https://i.yapx.ru/cEGTP.jpg",
    "https://i.yapx.ru/cEGTR.jpg",
    "https://i.yapx.ru/cEGTS.jpg",
    "https://i.yapx.ru/cEGTT.jpg",
    "https://i.yapx.ru/cEGTU.jpg",
    "https://i.yapx.ru/cEGTV.jpg",
    "https://i.yapx.ru/cEGTX.jpg",
    "https://i.yapx.ru/cEGTY.jpg",
    "https://i.yapx.ru/cEGTa.jpg"
]

last_message_time = None
MIN_INTERVAL = timedelta(minutes=20)  # минимум 20 минут между случайными сообщениями

# ------------------- функции -------------------
def send_reminder():
    global last_message_time
    if user_chat_id:
        bot.send_message(
            user_chat_id,
            "💊 пора принять таблетку!\n\nнажми «принял 💚» если уже выпил, или «отложить на час 🕒» если позже 💕",
            reply_markup=reminder_keyboard()
        )
        last_message_time = datetime.now()

def send_random_sweet_message(ignore_interval=False):
    global last_message_time
    now = datetime.now()
    if not ignore_interval and last_message_time and (now - last_message_time) < MIN_INTERVAL:
        return
    if user_chat_id:
        bot.send_message(user_chat_id, random.choice(sweet_messages))
        last_message_time = now

def send_random_meme(ignore_interval=False):
    global last_message_time
    now = datetime.now()
    if not ignore_interval and last_message_time and (now - last_message_time) < MIN_INTERVAL:
        return
    if user_chat_id:
        bot.send_photo(user_chat_id, random.choice(memes))
        last_message_time = now

def reminder_keyboard():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("💚 принял", callback_data="taken"),
        telebot.types.InlineKeyboardButton("🕒 отложить на час", callback_data="delay")
    )
    return markup

# ------------------- обработчики -------------------
@bot.message_handler(commands=['start'])
def start(message):
    global user_chat_id
    user_chat_id = message.chat.id
    bot.send_message(
        user_chat_id, 
        "привет, солнышко ☀️ я буду напоминать тебе о таблетках каждые 30 минут с 8 утра 💊\n\nа сегодня ты уже выпил таблетку?", 
        reply_markup=reminder_keyboard()
    )
    schedule_daily_reminders()

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "taken":
        bot.answer_callback_query(call.id, "умничка! 🌸 напоминания вернутся завтра 💖")
        scheduler.remove_all_jobs()
        schedule_daily_reminders(next_day=True)
        bot.send_message(OWNER_CHAT_ID, f"сашенька отметил, что выпил таблетку 💊")

    elif call.data == "delay":
        bot.answer_callback_query(call.id, "окей, напомню через час 💕")
        scheduler.remove_all_jobs()
        run_time = datetime.now() + timedelta(hours=1)
        scheduler.add_job(send_reminder, 'date', run_date=run_time, id="delayed_reminder")

# ------------------- эхо -------------------
@bot.message_handler(func=lambda message: True)
def playful_echo(message):
    """Если сообщение не команда, бот повторяет его с юмором и смайликами"""
    if message.text.startswith("/"):
        return

    playful_suffixes = [" 😜", " 🤭", " 🐾", "✨", "😂", "💖", "🤪", "🌸", "🐱"]
    playful_prefixes = ["о, ", "ага, ", "ммм, ", "эй, "]

    prefix = random.choice(playful_prefixes) if random.random() < 0.5 else ""
    suffix = random.choice(playful_suffixes) if random.random() < 0.7 else ""

    text = message.text
    if random.random() < 0.3:
        text = text.upper()
    elif random.random() < 0.3:
        text = text + "..."

    bot.send_message(message.chat.id, f"{prefix}{text}{suffix}")

# ------------------- планировщик -------------------
def schedule_daily_reminders(next_day=False):
    now = datetime.now()
    if next_day:
        start_time = now.replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=1)
    else:
        start_time = now

    scheduler.add_job(send_reminder, 'interval', minutes=30, start_date=start_time, id="interval_reminder")

    for _ in range(3):
        hour = random.randint(9, 22)
        minute = random.randint(0, 59)
        scheduler.add_job(send_random_sweet_message, 'cron', hour=hour, minute=minute)

    for _ in range(2):
        hour = random.randint(10, 22)
        minute = random.randint(0, 59)
        scheduler.add_job(send_random_meme, 'cron', hour=hour, minute=minute)

# ------------------- старт -------------------
scheduler.start()
bot.polling(none_stop=True)
