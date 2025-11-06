import telebot
import random
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import os
import logging
import requests

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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
]

memes = [
    "https://i.yapx.ru/cEGTF.jpg",
    "https://i.yapx.ru/cEGTH.jpg", 
    "https://i.yapx.ru/cEGTI.jpg",
]

last_message_time = None
MIN_INTERVAL = timedelta(seconds=10)

# ------------------- функции -------------------
def send_reminder():
    global last_message_time
    if user_chat_id:
        logger.info("🔴 ТЕСТ: Отправка напоминания о таблетке")
        try:
            bot.send_message(
                user_chat_id,
                "💊 ТЕСТ: пора принять таблетку!\n\nнажми «принял 💚» если уже выпил, или «отложить 🕒» если позже 💕",
                reply_markup=reminder_keyboard()
            )
            last_message_time = datetime.now()
        except Exception as e:
            logger.error(f"❌ Ошибка отправки напоминания: {e}")

def send_random_sweet_message():
    global last_message_time
    if user_chat_id:
        logger.info("🔴 ТЕСТ: Отправка милого сообщения")
        try:
            message = "💝 ТЕСТ: " + random.choice(sweet_messages)
            bot.send_message(user_chat_id, message)
            last_message_time = datetime.now()
            logger.info(f"✅ Милое сообщение отправлено: {message}")
        except Exception as e:
            logger.error(f"❌ Ошибка отправки милого сообщения: {e}")

def send_random_meme():
    global last_message_time
    if user_chat_id:
        logger.info("🔴 ТЕСТ: Попытка отправки мема")
        try:
            meme_url = random.choice(memes)
            logger.info(f"🔴 ТЕСТ: Пытаюсь отправить мем: {meme_url}")
            
            bot.send_photo(user_chat_id, meme_url, caption="📸 ТЕСТ: мем для тебя! 💖")
            last_message_time = datetime.now()
            logger.info(f"✅ Мем успешно отправлен: {meme_url}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки мема: {e}")
            try:
                bot.send_message(user_chat_id, "📸 ТЕСТ: не получилось отправить мем, но вот мысленный мем для тебя! 😊")
                logger.info("✅ Отправлено текстовое сообщение вместо мема")
            except Exception as e2:
                logger.error(f"❌ Ошибка отправки запасного сообщения: {e2}")

def reminder_keyboard():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("💚 принял", callback_data="taken"),
        telebot.types.InlineKeyboardButton("🕒 отложить", callback_data="delay")
    )
    return markup

def remove_reminder_jobs():
    """Удаляем только задания напоминаний"""
    for job_id in ["interval_reminder", "delayed_reminder"]:
        try:
            scheduler.remove_job(job_id)
        except:
            pass

def schedule_interval_reminders(start_delay_seconds=10):
    """Планируем регулярные интервальные напоминания"""
    remove_reminder_jobs()
    
    start_time = datetime.now() + timedelta(seconds=start_delay_seconds)
    
    scheduler.add_job(
        send_reminder, 
        'interval', 
        minutes=1,
        start_date=start_time,
        id="interval_reminder"
    )
    logger.info(f"🔴 ТЕСТ: Интервальные напоминания с {start_time} (через {start_delay_seconds}сек)")

def schedule_delayed_reminder():
    """Планируем одно отложенное напоминание и ПОТОМ снова интервальные"""
    remove_reminder_jobs()
    
    # Отложенное напоминание через 30 секунд
    run_time = datetime.now() + timedelta(seconds=30)
    scheduler.add_job(
        send_reminder, 
        'date', 
        run_date=run_time, 
        id="delayed_reminder"
    )
    
    # 🔴 ВАЖНО: после отложенного напоминания снова запускаем интервальные
    # но с задержкой 35 секунд (чтобы отложенное напоминание успело отправиться)
    scheduler.add_job(
        schedule_interval_reminders,
        'date',
        run_date=run_time + timedelta(seconds=5),
        kwargs={'start_delay_seconds': 0},  # начинаем сразу
        id="restart_intervals_after_delay"
    )
    
    logger.info(f"🔴 ТЕСТ: Отложенное напоминание на {run_time}, затем интервальные")

def schedule_content_messages():
    """Планируем мемы и милые сообщения"""
    # Сначала удаляем старые задания
    for i in range(10):
        for content_type in ['sweet_message', 'meme']:
            try:
                scheduler.remove_job(f"{content_type}_{i}")
            except:
                pass
    
    now = datetime.now()
    logger.info(f"🔴 ТЕСТ: Начинаю планирование контента в {now}")
    
    # 2 милых сообщения в ближайшие 2 минуты
    sweet_times = [
        now + timedelta(seconds=45),
        now + timedelta(minutes=1, seconds=30)
    ]
    
    for i, run_time in enumerate(sweet_times):
        scheduler.add_job(
            send_random_sweet_message, 
            'date', 
            run_date=run_time,
            id=f"sweet_message_{i}"
        )
        logger.info(f"🔴 ТЕСТ: Запланировано милое сообщение {i+1} на {run_time}")
    
    # 2 мема в ближайшие 3 минуты
    meme_times = [
        now + timedelta(minutes=1),
        now + timedelta(minutes=2, seconds=15)
    ]
    
    for i, run_time in enumerate(meme_times):
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
    
    schedule_interval_reminders()
    schedule_content_messages()
    
    show_jobs_info()

def show_jobs_info():
    """Показываем информацию о заданиях в логах"""
    jobs = scheduler.get_jobs()
    logger.info(f"🔴 ТЕСТ: Активно заданий: {len(jobs)}")
    for job in jobs:
        logger.info(f"🔴 ТЕСТ: Задание {job.id} - {job.next_run_time}")

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
        # Переносим напоминания на 30 секунд
        schedule_interval_reminders(start_delay_seconds=30)
        bot.send_message(OWNER_CHAT_ID, f"🔴 ТЕСТ: сашенька отметил таблетку")

    elif call.data == "delay":
        bot.answer_callback_query(call.id, "🔴 ТЕСТ: напомню через 30 секунд")
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None
        )
        # Планируем отложенное напоминание и затем интервальные
        schedule_delayed_reminder()

# ------------------- команды для тестирования -------------------
@bot.message_handler(commands=['test_meme'])
def test_meme(message):
    logger.info("🔴 ТЕСТ: Принудительная отправка мема по команде")
    send_random_meme()

@bot.message_handler(commands=['test_message'])
def test_message(message):
    logger.info("🔴 ТЕСТ: Принудительная отправка сообщения по команде")
    send_random_sweet_message()

@bot.message_handler(commands=['jobs'])
def show_jobs(message):
    jobs = scheduler.get_jobs()
    job_info = "🔴 ТЕСТ: Активные задания:\n\n"
    for job in jobs:
        job_info += f"• {job.id} - {job.next_run_time}\n"
    bot.send_message(message.chat.id, job_info)

# ------------------- эхо -------------------
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

    bot.send_message(message.chat.id, f"🔴 ТЕСТ: {prefix}{text}{suffix}")

# ------------------- старт -------------------
if __name__ == "__main__":
    scheduler.start()
    logger.info("🔴 ТЕСТ: Планировщик запущен")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logger.error(f"❌ Ошибка в боте: {e}")