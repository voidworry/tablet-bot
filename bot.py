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
    bot.send_message(user_chat_id, "привет, солнышко ☀️ я буду напоминать тебе о таблетках каждые 30 минут с 8 утра 💊\n\nа сегодня ты уже выпил таблетку?")
    bot.send_message(user_chat_id, "выбери, пожалуйста:", reply_markup=reminder_keyboard())
    schedule_daily_reminders()

@bot.message_handler(commands=['test'])
def test_mode(message):
    global user_chat_id
    user_chat_id = message.chat.id
    bot.send_message(user_chat_id, "🔧 запускаю тестовый режим 🔧\nнапоминания каждые 5 минут, мемы и фразы чаще, кнопки проверяемые 💕")

    scheduler.remove_all_jobs()
    now = datetime.now()
    start_time = now.replace(minute=0, second=0, microsecond=0)

    # тестовые напоминания каждые 5 минут
    scheduler.add_job(send_reminder, 'interval', minutes=5, start_date=start_time)
    # милые фразы каждые 2 минуты
    scheduler.add_job(send_random_sweet_message, 'interval', minutes=2, start_date=start_time)
    # мемы каждые 3 минуты
    scheduler.add_job(send_random_meme, 'interval', minutes=3, start_date=start_time)

    # callback для теста
    @bot.callback_query_handler(func=lambda call: True)
    def callback_query_test(call):
        if call.data == "taken":
            bot.answer_callback_query(call.id, "умничка! 🌸 тестовое напоминание вернется с начала следующего часа 💖")
            next_hour = (datetime.now() + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
            scheduler.remove_all_jobs()
            scheduler.add_job(send_reminder, 'interval', minutes=5, start_date=next_hour)
            bot.send_message(OWNER_CHAT_ID, f"сашенька отметил, что выпил таблетку 💊 (тест)")
        elif call.data == "delay":
            bot.answer_callback_query(call.id, "окей, напомню через 10 минут 💕")
            scheduler.add_job(send_reminder, 'date', run_date=datetime.now() + timedelta(minutes=10))

    bot.send_message(user_chat_id, "✅ тестовый режим активирован, следи за уведомлениями!")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "taken":
        bot.answer_callback_query(call.id, "умничка! 🌸 напоминания вернутся завтра 💖")
        schedule_daily_reminders()
        bot.send_message(OWNER_CHAT_ID, f"сашенька отметил, что выпил таблетку 💊")
    elif call.data == "delay":
        bot.answer_callback_query(call.id, "окей, напомню через час 💕")
        scheduler.add_job(send_reminder, 'date', run_date=datetime.now() + timedelta(hours=1))

# ------------------- планировщик -------------------
def schedule_daily_reminders():
    scheduler.remove_all_jobs()
    now = datetime.now()
    start_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
    if now > start_time:
        start_time += timedelta(days=1)
    scheduler.add_job(send_reminder, 'interval', minutes=30, start_date=start_time)

    # милые фразы по обычному графику
    for _ in range(3):
        hour = random.randint(9, 22)
        minute = random.randint(0, 59)
        scheduler.add_job(send_random_sweet_message, 'cron', hour=hour, minute=minute)

    # мемы по обычному графику
    for _ in range(2):
        hour = random.randint(10, 22)
        minute = random.randint(0, 59)
        scheduler.add_job(send_random_meme, 'cron', hour=hour, minute=minute)

# ------------------- старт -------------------
scheduler.start()
bot.polling(none_stop=True)


