import telebot
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
last_message_time = None

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
        message.chat.id, 
        "привет, солнышко ☀️\nя буду напоминать тебе о таблетках каждый день.\nпрости, а сегодня ты уже выпил таблетку?",
        reply_markup=reminder_keyboard()
    )
    schedule_reminders_after_start()

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global user_chat_id
    if call.data == "taken":
        bot.answer_callback_query(call.id, "умничка! 🌸 напоминания вернутся завтра с 8 утра 💖")
        schedule_next_day_reminders()
        bot.send_message(OWNER_CHAT_ID, f"Сашенька отметил, что выпил таблетку 💊")
    elif call.data == "delay":
        bot.answer_callback_query(call.id, "окей, напомню через час 💕")
        scheduler.remove_all_jobs()
        scheduler.add_job(send_reminder, 'date', run_date=datetime.now() + timedelta(hours=1))

# ------------------- планировщик -------------------
def schedule_reminders_after_start():
    """напоминания каждые 30 минут после запуска бота до нажатия 'принял'"""
    scheduler.remove_all_jobs()
    now = datetime.now()
    scheduler.add_job(send_reminder, 'interval', minutes=30, start_date=now)

def schedule_next_day_reminders():
    """следующие напоминания с 8 утра следующего дня"""
    scheduler.remove_all_jobs()
    now = datetime.now()
    start_time = now.replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=1)
    scheduler.add_job(send_reminder, 'interval', minutes=30, start_date=start_time)

# ------------------- старт -------------------
scheduler.start()
bot.polling(none_stop=True)

