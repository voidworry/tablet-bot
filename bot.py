import telebot
import random
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import os
import logging
import time

# Минимальное логирование для скорости
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# ------------------- настройки -------------------
TOKEN = os.getenv("TOKEN")
OWNER_CHAT_ID = os.getenv("OWNER_CHAT_ID") 

if not TOKEN or not OWNER_CHAT_ID:
    raise ValueError("Проверь переменные окружения!")

OWNER_CHAT_ID = int(OWNER_CHAT_ID)

# 🔴 ОПТИМИЗАЦИЯ: быстрый бот с многопоточностью
bot = telebot.TeleBot(TOKEN, threaded=True, num_threads=5)
scheduler = BackgroundScheduler()
user_chat_id = None

# ------------------- контент (предзагружен) -------------------
SWEET_MESSAGES = [
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
    "🪷 я верю в тебя, всегда и во всём 🌸",
]

MEMES = [
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
]

# 🔴 ОПТИМИЗАЦИЯ: предсозданные клавиатуры
WELCOME_KB = telebot.types.InlineKeyboardMarkup()
WELCOME_KB.add(
    telebot.types.InlineKeyboardButton("💚 уже принял", callback_data="already_taken"),
    telebot.types.InlineKeyboardButton("🤔 еще нет", callback_data="not_yet")
)

REMINDER_KB = telebot.types.InlineKeyboardMarkup()
REMINDER_KB.add(
    telebot.types.InlineKeyboardButton("💚 принял", callback_data="taken"),
    telebot.types.InlineKeyboardButton("🕒 отложить на час", callback_data="delay")
)

last_message_time = None

# ------------------- оптимизированные функции -------------------
def get_moscow_time():
    return datetime.now() + timedelta(hours=3)  # UTC+3

def send_reminder():
    global last_message_time
    if user_chat_id:
        try:
            bot.send_message(user_chat_id, "💊 пора принять таблетку!\n\nнажми «принял 💚» или «отложить на час 🕒» 💕", reply_markup=REMINDER_KB)
            last_message_time = get_moscow_time()
        except: pass

def send_random_sweet_message():
    global last_message_time
    if user_chat_id:
        try:
            bot.send_message(user_chat_id, random.choice(SWEET_MESSAGES))
            last_message_time = get_moscow_time()
        except: pass

def send_random_meme():
    global last_message_time
    if user_chat_id:
        try:
            bot.send_photo(user_chat_id, random.choice(MEMES))
            last_message_time = get_moscow_time()
        except:
            try: bot.send_message(user_chat_id, "📸 мысленный мем для тебя! 😊")
            except: pass

def remove_reminder_jobs():
    for job_id in ["interval_reminder", "delayed_reminder", "first_reminder"]:
        try: scheduler.remove_job(job_id)
        except: pass

def schedule_interval_reminders(start_delay_minutes=0):
    remove_reminder_jobs()
    now = get_moscow_time()
    
    if start_delay_minutes > 0:
        start_time = now + timedelta(minutes=start_delay_minutes)
    else:
        start_time = now + timedelta(minutes=30) if now.hour >= 8 else now.replace(hour=8, minute=0, second=0)
    
    scheduler.add_job(send_reminder, 'interval', minutes=30, start_date=start_time, id="interval_reminder")

def schedule_first_reminder():
    remove_reminder_jobs()
    run_time = get_moscow_time() + timedelta(minutes=30)
    scheduler.add_job(send_reminder, 'date', run_date=run_time, id="first_reminder")
    scheduler.add_job(schedule_interval_reminders, 'date', run_date=run_time + timedelta(minutes=5), kwargs={'start_delay_minutes': 0})

def schedule_delayed_reminder():
    remove_reminder_jobs()
    run_time = get_moscow_time() + timedelta(hours=1)
    scheduler.add_job(send_reminder, 'date', run_date=run_time, id="delayed_reminder")
    scheduler.add_job(schedule_interval_reminders, 'date', run_date=run_time + timedelta(minutes=5), kwargs={'start_delay_minutes': 0})

def schedule_content_messages():
    # Быстрая очистка
    for i in range(5):
        for content_type in ['sweet_message', 'meme']:
            try: scheduler.remove_job(f"{content_type}_{i}")
            except: pass
    
    now = get_moscow_time()
    today = now.date()
    
    # Планируем контент на сегодня
    for i in range(3):  # 3 сообщения
        hour, minute = random.randint(9, 22), random.randint(0, 59)
        run_time = datetime(today.year, today.month, today.day, hour, minute, 0)
        if run_time > now:
            scheduler.add_job(send_random_sweet_message, 'date', run_date=run_time, id=f"sweet_message_{i}")
    
    for i in range(2):  # 2 мема
        hour, minute = random.randint(10, 22), random.randint(0, 59)
        run_time = datetime(today.year, today.month, today.day, hour, minute, 0)
        if run_time > now:
            scheduler.add_job(send_random_meme, 'date', run_date=run_time, id=f"meme_{i}")
    
    # Автоперепланировка на завтра
    tomorrow = today + timedelta(days=1)
    next_day_time = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 1, 0)
    scheduler.add_job(schedule_content_messages, 'date', run_date=next_day_time, id="reschedule_content")

# ------------------- обработчики -------------------
@bot.message_handler(commands=['start'])
def start(message):
    global user_chat_id
    user_chat_id = message.chat.id
    
    now = get_moscow_time()
    greeting = "привет, солнышко ☀️ я буду напоминать тебе о таблетках каждые 30 минут с 8 утра 💊\n\nты уже выпил таблетку?" if now.hour >= 8 else "привет, солнышко ☀️ я буду напоминать тебе о таблетках каждые 30 минут 💊\n\nты уже выпил сегодняшнюю таблетку?"
    
    bot.send_message(user_chat_id, greeting, reply_markup=WELCOME_KB)
    schedule_content_messages()

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        if call.data == "already_taken":
            bot.answer_callback_query(call.id, "умничка! 💖")
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            schedule_interval_reminders(start_delay_minutes=24*60)
            bot.send_message(call.message.chat.id, "💚 умничка! завтра в 8 утра 💖")
            bot.send_message(OWNER_CHAT_ID, "сашенька отметил, что выпил таблетку 💊")

        elif call.data == "not_yet":
            bot.answer_callback_query(call.id, "окей 💕")
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            schedule_first_reminder()
            bot.send_message(call.message.chat.id, "💊 напомню через полчаса! 🌸")

        elif call.data == "taken":
            bot.answer_callback_query(call.id, "умничка! 💖")
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            schedule_interval_reminders(start_delay_minutes=24*60)
            bot.send_message(OWNER_CHAT_ID, "сашенька отметил, что выпил таблетку 💊")

        elif call.data == "delay":
            bot.answer_callback_query(call.id, "окей 💕")
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            bot.send_message(call.message.chat.id, "🕒 напомню через час 💕")
            schedule_delayed_reminder()
    except: pass

# ------------------- команды для отладки -------------------
@bot.message_handler(commands=['ping'])
def ping(message):
    start_time = time.time()
    bot.send_message(message.chat.id, "🏓 понг!")
    response_time = round((time.time() - start_time) * 1000, 2)
    status = "⚠️ МЕДЛЕННО" if response_time > 1000 else "✅ НОРМА" if response_time > 100 else "🚀 БЫСТРО"
    bot.send_message(message.chat.id, f"⏱ {response_time} мс | {status}")

@bot.message_handler(commands=['test_meme'])
def test_meme(message):
    send_random_meme()

@bot.message_handler(commands=['test_message'])
def test_message(message):
    send_random_sweet_message()

@bot.message_handler(commands=['jobs'])
def show_jobs(message):
    jobs = scheduler.get_jobs()
    job_info = f"Активных заданий: {len(jobs)}\n"
    for job in jobs[:5]:  # Показываем только первые 5
        job_info += f"• {job.id}\n"
    bot.send_message(message.chat.id, job_info)

@bot.message_handler(commands=['status'])
def status(message):
    jobs = scheduler.get_jobs()
    status_text = f"""📊 Статус:
• Заданий: {len(jobs)}
• Пользователь: {'✅' if user_chat_id else '❌'}
• Время МСК: {get_moscow_time().strftime('%H:%M')}"""
    bot.send_message(message.chat.id, status_text)

@bot.message_handler(commands=['restart'])
def restart_bot(message):
    scheduler.remove_all_jobs()
    schedule_content_messages()
    bot.send_message(message.chat.id, "🔄 Перезапущено!")
    start(message)

# ------------------- эхо -------------------
@bot.message_handler(func=lambda message: True)
def playful_echo(message):
    if message.text.startswith("/"): return
    
    text = message.text
    if random.random() < 0.3: text = text.upper()
    elif random.random() < 0.3: text = text + "..."
    
    suffix = random.choice([" 😜", " 🤭", " 🐾", " ✨", " 💖", " 🌸"])
    bot.send_message(message.chat.id, f"{text}{suffix}")

# ------------------- старт -------------------
if __name__ == "__main__":
    scheduler.start()
    print("🚀 Бот запущен!")
    try:
        bot.polling(none_stop=True, interval=1, timeout=15)
    except Exception as e:
        print(f"Ошибка: {e}")