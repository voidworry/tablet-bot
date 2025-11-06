import telebot
import random
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import os
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
]

memes = [
    "https://i.yapx.ru/cEGTF.jpg",
    "https://i.yapx.ru/cEGTH.jpg",
    "https://i.yapx.ru/cEGTI.jpg",
]

last_message_time = None
MIN_INTERVAL = timedelta(seconds=10)  # 🔴 ТЕСТ: 10 секунд между сообщениями

# ------------------- функции -------------------
def send_reminder():
    global last_message_time
    if user_chat_id:
        logger.info("🔴 ТЕСТ: Отправка напоминания о таблетке")
        bot.send_message(
            user_chat_id,
            "💊 ТЕСТ: пора принять таблетку!\n\nнажми «принял 💚» если уже выпил, или «отложить 🕒» если позже 💕",
            reply_markup=reminder_keyboard()
        )
        last_message_time = datetime.now()

def send_random_sweet_message(ignore_interval=False):
    global last_message_time
    now = datetime.now()
    if not ignore_interval and last_message_time and (now - last_message_time) < MIN_INTERVAL:
        return
    if user_chat_id:
        logger.info("🔴 ТЕСТ: Отправка милого сообщения")
        bot.send_message(user_chat_id, "💝 ТЕСТ: " + random.choice(sweet_messages))
        last_message_time = now

def send_random_meme(ignore_interval=False):
    global last_message_time
    now = datetime.now()
    if not ignore_interval and last_message_time and (now - last_message_time) < MIN_INTERVAL:
        return
    if user_chat_id:
        logger.info("🔴 ТЕСТ: Отправка мема")
        bot.send_photo(user_chat_id, random.choice(memes), caption="📸 ТЕСТ: мем")
        last_message_time = now

def reminder_keyboard():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("💚 принял", callback_data="taken"),
        telebot.types.InlineKeyboardButton("🕒 отложить", callback_data="delay")  # 🔴 ТЕСТ: без указания времени
    )
    return markup

def remove_reminder_jobs():
    """Удаляем только задания напоминаний, не затрагивая контент"""
    try:
        scheduler.remove_job("interval_reminder")
    except:
        pass
    try:
        scheduler.remove_job("delayed_reminder")
    except:
        pass

def schedule_daily_reminders(next_day=False):
    """Планируем ежедневные напоминания (для теста - короткие интервалы)"""
    global user_chat_id
    now = datetime.now()
    
    # 🔴 ТЕСТ: короткие интервалы для тестирования
    if next_day:
        start_time = now + timedelta(seconds=30)  # 🔴 ТЕСТ: через 30 секунд
    else:
        start_time = now + timedelta(seconds=10)  # 🔴 ТЕСТ: через 10 секунд
    
    logger.info(f"🔴 ТЕСТ: Планируем напоминания с {start_time}")
    
    # Удаляем старые напоминания
    remove_reminder_jobs()
    
    # 🔴 ТЕСТ: интервал 1 минута вместо 30
    scheduler.add_job(
        send_reminder, 
        'interval', 
        minutes=1,  # 🔴 ТЕСТ: 1 минута
        start_date=start_time,
        id="interval_reminder"
    )

def schedule_content_messages():
    """Планируем мемы и милые сообщения (для теста - короткие интервалы)"""
    # Удаляем старые задания контента
    for i in range(5):
        try:
            scheduler.remove_job(f"sweet_message_{i}")
            scheduler.remove_job(f"meme_{i}")
        except:
            pass
    
    # 🔴 ТЕСТ: планируем на ближайшие минуты
    now = datetime.now()
    
    # 3 милых сообщения в течение 5 минут
    for i in range(3):
        run_time = now + timedelta(minutes=i*2, seconds=30)  # 🔴 ТЕСТ: через 0.5, 2.5, 4.5 минут
        scheduler.add_job(
            send_random_sweet_message, 
            'date', 
            run_date=run_time,
            id=f"sweet_message_{i}"
        )
        logger.info(f"🔴 ТЕСТ: Запланировано милое сообщение {i+1} на {run_time}")
    
    # 2 мема в течение 5 минут  
    for i in range(2):
        run_time = now + timedelta(minutes=i*2 + 1, seconds=15)  # 🔴 ТЕСТ: через 1.25, 3.25 минут
        scheduler.add_job(
            send_random_meme, 
            'date', 
            run_date=run_time,
            id=f"meme_{i}"
        )
        logger.info(f"🔴 ТЕСТ: Запланирован мем {i+1} на {run_time}")

# ------------------- обработчики -------------------
@bot.message_handler(commands=['start'])
def start(message):
    global user_chat_id
    user_chat_id = message.chat.id
    logger.info(f"🔴 ТЕСТ: Бот запущен пользователем {user_chat_id}")
    
    bot.send_message(
        user_chat_id, 
        "🔴 ТЕСТОВЫЙ РЕЖИМ\nпривет! я буду напоминать о таблетках каждую минуту 💊\n\nты уже выпил таблетку?", 
        reply_markup=reminder_keyboard()
    )
    
    # Планируем напоминания и контент
    schedule_daily_reminders()
    schedule_content_messages()

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    logger.info(f"🔴 ТЕСТ: Обработка callback: {call.data}")
    
    if call.data == "taken":
        bot.answer_callback_query(call.id, "🔴 ТЕСТ: принял! напоминания через 30 сек")
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None
        )
        # 🔴 ТЕСТ: переносим на 30 секунд вместо след дня
        schedule_daily_reminders(next_day=True)
        bot.send_message(OWNER_CHAT_ID, f"🔴 ТЕСТ: сашенька отметил таблетку")

    elif call.data == "delay":
        bot.answer_callback_query(call.id, "🔴 ТЕСТ: напомню через 30 секунд")
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None
        )
        # Удаляем текущие напоминания
        remove_reminder_jobs()
        
        # 🔴 ТЕСТ: откладываем на 30 секунд вместо часа
        run_time = datetime.now() + timedelta(seconds=30)
        scheduler.add_job(
            send_reminder, 
            'date', 
            run_date=run_time, 
            id="delayed_reminder"
        )
        logger.info(f"🔴 ТЕСТ: Напоминание отложено на {run_time}")

# ------------------- команды для тестирования -------------------
@bot.message_handler(commands=['test_meme'])
def test_meme(message):
    send_random_meme(ignore_interval=True)

@bot.message_handler(commands=['test_message'])
def test_message(message):
    send_random_sweet_message(ignore_interval=True)

@bot.message_handler(commands=['test_reminder'])
def test_reminder(message):
    send_reminder()

@bot.message_handler(commands=['jobs'])
def show_jobs(message):
    jobs = scheduler.get_jobs()
    job_info = "🔴 ТЕСТ: Активные задания:\n\n"
    for job in jobs:
        job_info += f"• {job.id} - {job.next_run_time}\n"
    bot.send_message(message.chat.id, job_info)

@bot.message_handler(commands=['clear_jobs'])
def clear_jobs(message):
    scheduler.remove_all_jobs()
    bot.send_message(message.chat.id, "🔴 ТЕСТ: Все задания очищены")

@bot.message_handler(commands=['restart'])
def restart(message):
    bot.send_message(message.chat.id, "🔴 ТЕСТ: Перезапускаем планировщик...")
    scheduler.remove_all_jobs()
    schedule_daily_reminders()
    schedule_content_messages()

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

    bot.send_message(message.chat.id, f"🔴 ТЕСТ: {prefix}{text}{suffix}")

# ------------------- старт -------------------
if __name__ == "__main__":
    scheduler.start()
    logger.info("🔴 ТЕСТ: Планировщик запущен")
    bot.polling(none_stop=True)
