import telebot
import random
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import os

# ------------------- Настройки -------------------
TOKEN = os.getenv("TOKEN")
OWNER_CHAT_ID = os.getenv("OWNER_CHAT_ID") 

if not TOKEN:
    raise ValueError("TOKEN не найден в переменных окружениях!")
if not OWNER_CHAT_ID:
    raise ValueError("OWNER_CHAT_ID не найден в переменных окружениях!")

OWNER_CHAT_ID = int(OWNER_CHAT_ID)
print("TOKEN и OWNER_CHAT_ID загружены успешно.")

bot = telebot.TeleBot(TOKEN)
scheduler = BackgroundScheduler()
user_chat_id = None
reminder_job = None  # для интервала 30 минут

# ------------------- Контент -------------------
sweet_messages = [
    "💖 напоминáю, я тебя люблю ❣️",
    "🐾 ты у меня самый замечательный ✨",
    "☀️ горжусь тобой, что заботишься о себе 🌸",
    "🧸 надеюсь, ты чувствуешь себя хорошо >.<",
    "🌼 твоя забота о себе делает мой день лучше 🌷",
    "💛 ты самый смелый и сильный ⭐️",
    "🌸 моё сердце радуется, когда думаю о тебе 🫶",
    "🐱 не забывай улыбáться, ты чудо ❣️",
    "✨ каждый день с тобой особенный 🌟",
    "💐 ты заслуживаешь только счастья 🍀",
    "🌞 твоя энергия делает мир ярче ☀️",
    "🫂 помни, я всегда рядом мысленно с тобой 💫",
    "💌 ты делаешь меня счастливой просто своим существованием 🐾",
    "🎀 ты — моя радость и вдохновение 🌸",
    "🥰 я горжусь тобой за каждое маленькое усилиё ✨",
    "💫 ты такой уникальный, что словами не описать ❣️",
    "🌷 твоя доброта делает мир лучше 🐱",
    "💭 думаю о тебе и улыбаюсь 🌸",
    "🧡 ты наполняешь мой день теплом 🌞",
    "🐝 ты - моё счастьё ⭐️",
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

# ------------------- Функции -------------------
def send_reminder():
    global last_message_time, reminder_job
    if user_chat_id:
        bot.send_message(
            user_chat_id,
            "💊 пора принять таблетку!\n\nнажми «принял 💚» если уже выпил, или «отложить на час 🕒» если позже 💕",
            reply_markup=reminder_keyboard()
        )
        last_message_time = datetime.now()
        # Если это был отложенное напоминание, перезапустить интервал 30 минут
        if reminder_job:
            scheduler.remove_job(reminder_job.id)
        reminder_job = scheduler.add_job(send_reminder, 'interval', minutes=30, start_date=datetime.now() + timedelta(minutes=30))

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

# ------------------- Обработчики -------------------
@bot.message_handler(commands=['start'])
def start(message):
    global user_chat_id
    user_chat_id = message.chat.id
    bot.send_message(
        message.chat.id,
        "Привет, солнышко ☀️ я буду напоминать тебе о таблетках каждый день 💊\n\nА сегодня ты уже выпил таблетку?",
        reply_markup=reminder_keyboard()
    )

@bot.message_handler(commands=['test'])
def test_all_functions(message):
    global user_chat_id
    user_chat_id = message.chat.id
    bot.send_message(user_chat_id, "🔧 тестирую функции бота 🔧")
    
    # Случайная милая фраза
    send_random_sweet_message(ignore_interval=True)
    
    # Случайный мем
    send_random_meme(ignore_interval=True)
    
    # Тестовое напоминание с кнопками
    bot.send_message(
        user_chat_id,
        "💊 тестовое напоминание! Нажми кнопку, чтобы проверить реакцию бота:",
        reply_markup=reminder_keyboard()
    )
    
    bot.send_message(user_chat_id, "✅ тест завершён! Нажми 💚, чтобы проверить уведомление на OWNER_CHAT_ID.")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global reminder_job
    if call.data == "taken":
        bot.answer_callback_query(call.id, "умничка! 🌸 напоминания вернутся завтра 💖")
        bot.send_message(OWNER_CHAT_ID, f"сашенька отметил, что выпил таблетку 💊")
        # Запланировать на завтра с 8 утра
        schedule_daily_reminders(start_from_next_day=True)
        if reminder_job:
            scheduler.remove_job(reminder_job.id)
            reminder_job = None
    elif call.data == "delay":
        bot.answer_callback_query(call.id, "окей, напомню через час 💕")
        if reminder_job:
            scheduler.remove_job(reminder_job.id)
        # Новое отложенное напоминание через час
        reminder_job = scheduler.add_job(send_reminder, 'date', run_date=datetime.now() + timedelta(hours=1))

# ------------------- Эхо -------------------
@bot.message_handler(func=lambda message: True)
def playful_echo(message):
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

# ------------------- Планировщик -------------------
def schedule_daily_reminders(start_from_next_day=False):
    global reminder_job
    scheduler.remove_all_jobs()
    now = datetime.now()
    
    start_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
    if start_from_next_day or now >= start_time:
        start_time += timedelta(days=1)
    
    reminder_job = scheduler.add_job(send_reminder, 'interval', minutes=30, start_date=start_time)

# ------------------- Старт -------------------
scheduler.start()
bot.polling(none_stop=True)
