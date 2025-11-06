import telebot
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import os

# ------------------- Настройки -------------------
TOKEN = os.getenv("TOKEN")
OWNER_CHAT_ID = os.getenv("OWNER_CHAT_ID") 

if not TOKEN:
    raise ValueError("TOKEN не найден в переменных окружения!")
if not OWNER_CHAT_ID:
    raise ValueError("OWNER_CHAT_ID не найден в переменных окружения!")

OWNER_CHAT_ID = int(OWNER_CHAT_ID)
print("TOKEN и OWNER_CHAT_ID загружены успешно.")

bot = telebot.TeleBot(TOKEN)
scheduler = BackgroundScheduler()
user_chat_id = None

# ------------------- Контент -------------------
sweet_messages = [
    "💖 напоминаю, я тебя люблю ❣️",
    "🐾 ты у меня самый замечательный ✨",
    "☀️ горжусь тобой, что заботишься о себе 🌸",
    "🧸 надеюсь, ты чувствуешь себя хорошо >.<",
    "🌼 твоя забота о себе делает мой день лучше 🌷",
    "💛 ты самый смелый и сильный ⭐️",
    "🌸 моё сердце радуётся, когда думаю о тебе 🫶",
    "🐱 не забывай улыбаться, ты чудо ❣️",
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
    "🐝 ты - моё счастье ⭐️",
    "🍀 желаю тебе сегодня только удачи и радости ✨",
    "🎶 ты сводишь меня с ума 🐾",
    "💎 ты - моё сокровище ❣️",
    "🌹 твоя улыбка — лучик солнца ☀️",
    "🪷 я верю в тебя, всегда и во всём 🌸"
]

last_message_time = None
MIN_INTERVAL = timedelta(minutes=20)  # минимум 20 минут между случайными сообщениями

# ------------------- Функции -------------------
def send_reminder():
    global last_message_time
    if user_chat_id:
        bot.send_message(
            user_chat_id,
            "💊 пора принять таблетку!\n\nнажми «принял 💚» если уж выпил, или «отложить на час 🕒» если позже 💕",
            reply_markup=reminder_keyboard()
        )
        last_message_time = datetime.now()

def reminder_keyboard():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("💚 принял", callback_data="taken"),
        telebot.types.InlineKeyboardButton("🕒 отложить на час", callback_data="delay")
    )
    return markup

def schedule_reminders_interval(start_now=False):
    """Запуск напоминаний каждые 30 минут. Если start_now=True, первый запуск через 30 мин от текущего времени"""
    scheduler.remove_all_jobs()
    if start_now:
        scheduler.add_job(send_reminder, 'interval', minutes=30, next_run_time=datetime.now() + timedelta(minutes=30))
    else:
        # старт с 8 утра следующего дня
        now = datetime.now()
        start_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
        if now > start_time:
            start_time += timedelta(days=1)
        scheduler.add_job(send_reminder, 'interval', minutes=30, start_date=start_time)

# ------------------- Обработчики -------------------
@bot.message_handler(commands=['start'])
def start(message):
    global user_chat_id
    user_chat_id = message.chat.id

    # Стартовое приветствие с кнопками
    bot.send_message(
        user_chat_id,
        "Привет, солнышко ☀️\nЯ буду напоминать тёбё о таблетках каждые 30 минут 💊\n\nА ты сёгдня уже выпил таблетку?",
        reply_markup=reminder_keyboard()
    )

    # Запуск интервала через 30 минут
    schedule_reminders_interval(start_now=True)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "taken":
        bot.answer_callback_query(call.id, "Умничка! 🌸 Напоминания вернутся завтра 💖")
        schedule_reminders_interval(start_now=False)  # следующий день с 8 утра
        bot.send_message(OWNER_CHAT_ID, f"Сашенька отметил, что выпил таблетку 💊")
    elif call.data == "delay":
        bot.answer_callback_query(call.id, "Окей, напомню через час 💕")
        # удаляем текущее интервальное напоминание
        scheduler.remove_all_jobs()
        # запланировать через час
        scheduler.add_job(send_reminder, 'date', run_date=datetime.now() + timedelta(hours=1))
        # после напоминания продолжить интервал каждые 30 минут
        scheduler.add_job(schedule_reminders_interval, 'date', run_date=datetime.now() + timedelta(hours=1), args=[True])

# ------------------- Старт -------------------
scheduler.start()
bot.polling(none_stop=True)
