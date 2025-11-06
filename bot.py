import telebot
import random
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import os
import logging
import requests
from zoneinfo import ZoneInfo
import time

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

try:
    MOSCOW_TZ = ZoneInfo("Europe/Moscow")
except:
    logger.warning("ZoneInfo не доступен, используем UTC+3")
    MOSCOW_TZ = None

bot = telebot.TeleBot(TOKEN)
scheduler = BackgroundScheduler(timezone=MOSCOW_TZ) if MOSCOW_TZ else BackgroundScheduler()
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
    "✨ каждый день с тобой особенный 🌟",
    "💐 ты заслуживаешь только счастья 🍀",
    "🌞 твоя энергия делает мир ярче ☀️",
    "💌 ты делаешь меня счастливой просто своим существованием 🐾",
    "🎀 ты — моя радость и вдохновение 🌸",
    "💫 ты такой уникальный, что словами не описать ❣️",
    "💭 думаю о тебе и улыбаюсь 🌸",
    "🧡 ты наполняешь мой день теплом 🌞"
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
    "https://i.yapx.ru/cEGTR.jpg"
]

# ------------------- основные функции -------------------
def get_moscow_time():
    """Получаем текущее время в Москве"""
    if MOSCOW_TZ:
        return datetime.now(MOSCOW_TZ)
    else:
        return datetime.utcnow() + timedelta(hours=3)

def safe_send_message(chat_id, text, reply_markup=None, max_retries=3):
    """Безопасная отправка сообщения с повторными попытками"""
    for attempt in range(max_retries):
        try:
            if reply_markup:
                bot.send_message(chat_id, text, reply_markup=reply_markup)
            else:
                bot.send_message(chat_id, text)
            return True
        except Exception as e:
            logger.warning(f"Ошибка отправки (попытка {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
    return False

def safe_send_photo(chat_id, photo_url, max_retries=3):
    """Безопасная отправка фото с повторными попытками"""
    for attempt in range(max_retries):
        try:
            bot.send_photo(chat_id, photo_url)
            return True
        except Exception as e:
            logger.warning(f"Ошибка отправки фото (попытка {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
    return False

def send_reminder():
    """Отправка напоминания о таблетке"""
    if user_chat_id:
        logger.info("Отправка напоминания о таблетке")
        safe_send_message(
            user_chat_id,
            "💊 пора принять таблетку!\n\nнажми «принял 💚» если уже выпил, или «отложить на час 🕒» если позже 💕",
            reply_markup=reminder_keyboard()
        )

def send_random_content():
    """Случайная отправка либо милого сообщения, либо мема"""
    if not user_chat_id:
        return
        
    if random.random() < 0.6:  # 60% вероятность сообщения
        logger.info("Отправка милого сообщения")
        safe_send_message(user_chat_id, random.choice(sweet_messages))
    else:  # 40% вероятность мема
        logger.info("Отправка мема")
        if not safe_send_photo(user_chat_id, random.choice(memes)):
            safe_send_message(user_chat_id, "📸 мысленный мем для тебя! 😊")

def welcome_keyboard():
    """Клавиатура для приветственного сообщения"""
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("💚 уже принял", callback_data="already_taken"),
        telebot.types.InlineKeyboardButton("💊 еще нет", callback_data="not_yet")
    )
    return markup

def reminder_keyboard():
    """Клавиатура для напоминания"""
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("💚 принял", callback_data="taken"),
        telebot.types.InlineKeyboardButton("🕒 отложить на час", callback_data="delay")
    )
    return markup

def start_reminder_system():
    """Запуск системы напоминаний"""
    remove_reminder_jobs()
    
    # Начинаем напоминания через 30 минут и потом каждые 30 минут
    start_time = get_moscow_time() + timedelta(minutes=30)
    
    scheduler.add_job(
        send_reminder, 
        'interval', 
        minutes=30,
        start_date=start_time,
        id="interval_reminder"
    )
    logger.info(f"Система напоминаний запущена, первое напоминание в {start_time}")

def remove_reminder_jobs():
    """Удаляем задания напоминаний"""
    for job_id in ["interval_reminder", "delayed_reminder"]:
        try:
            scheduler.remove_job(job_id)
        except:
            pass

def schedule_delayed_reminder():
    """Отложенное напоминание через час"""
    remove_reminder_jobs()
    
    run_time = get_moscow_time() + timedelta(hours=1)
    scheduler.add_job(send_reminder, 'date', run_date=run_time, id="delayed_reminder")
    
    # Через час после отложенного напоминания возвращаем обычный режим
    scheduler.add_job(
        start_reminder_system,
        'date', 
        run_date=run_time + timedelta(minutes=5)
    )
    
    logger.info(f"Напоминание отложено до {run_time}")

def schedule_daily_content():
    """Планируем ежедневный контент"""
    # Удаляем старые задания
    for i in range(10):
        try:
            scheduler.remove_job(f"daily_content_{i}")
        except:
            pass
    
    now = get_moscow_time()
    today = now.date()
    
    # 4 случайных отправки в день с 9 до 22
    for i in range(4):
        hour = random.randint(9, 22)
        minute = random.randint(0, 59)
        
        if MOSCOW_TZ:
            run_time = datetime(today.year, today.month, today.day, hour, minute, 0, tzinfo=MOSCOW_TZ)
        else:
            run_time = datetime(today.year, today.month, today.day, hour, minute, 0) + timedelta(hours=3)
        
        if run_time > now:
            scheduler.add_job(
                send_random_content, 
                'date', 
                run_date=run_time,
                id=f"daily_content_{i}"
            )
            logger.info(f"Контент запланирован на {run_time}")

# ------------------- обработчики -------------------
@bot.message_handler(commands=['start'])
def start(message):
    global user_chat_id
    user_chat_id = message.chat.id
    logger.info(f"Бот запущен пользователем {user_chat_id}")
    
    greeting = "привет, солнышко! ☀️ я буду напоминать тебе о таблетках 💊\n\nты уже выпил сегодняшнюю таблетку?"
    
    safe_send_message(user_chat_id, greeting, reply_markup=welcome_keyboard())
    schedule_daily_content()

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    logger.info(f"Обработка callback: {call.data}")
    
    try:
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None
        )
    except:
        pass

    # Определяем ответ и действие для каждого случая
    responses = {
        "already_taken": ("💚 умничка! 🌸 напоминания вернутся завтра в 8 утра 💖", "start_tomorrow"),
        "taken": ("💚 умничка! 🌸 напоминания вернутся завтра в 8 утра 💖", "start_tomorrow"), 
        "not_yet": ("💊 хорошо! напомню тебе через полчаса! 🌸", "start_now"),
        "delay": ("🕒 окей, напомню через час 💕", "delay_hour")
    }

    if call.data in responses:
        response, action = responses[call.data]
        
        # Выполняем соответствующее действие
        if action == "start_tomorrow":
            tomorrow_8am = get_moscow_time().replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=1)
            scheduler.add_job(start_reminder_system, 'date', run_date=tomorrow_8am)
            safe_send_message(OWNER_CHAT_ID, "сашенька отметил, что выпил таблетку 💊")
        elif action == "start_now":
            start_reminder_system()
        elif action == "delay_hour":
            schedule_delayed_reminder()
        
        # Отправляем ответ пользователю
        bot.answer_callback_query(call.id, response)
        safe_send_message(call.message.chat.id, response)

# ------------------- управляющие команды -------------------
@bot.message_handler(commands=['status'])
def status(message):
    """Текущий статус бота"""
    jobs = scheduler.get_jobs()
    status_text = f"""
📊 Статус бота:
• Активных заданий: {len(jobs)}
• Пользователь: {'подключен' if user_chat_id else 'не подключен'}
• Время МСК: {get_moscow_time().strftime('%H:%M:%S')}
    """
    safe_send_message(message.chat.id, status_text)

@bot.message_handler(commands=['jobs'])
def show_jobs(message):
    """Показать все активные задания с временем"""
    jobs = scheduler.get_jobs()
    
    if not jobs:
        safe_send_message(message.chat.id, "📭 Нет активных заданий")
        return
    
    now = get_moscow_time()
    job_info = "📅 **Активные задания:**\n\n"
    
    for i, job in enumerate(jobs, 1):
        next_run = job.next_run_time.astimezone(MOSCOW_TZ) if MOSCOW_TZ else job.next_run_time + timedelta(hours=3)
        time_until = next_run - now
        hours_until = time_until.total_seconds() // 3600
        minutes_until = (time_until.total_seconds() % 3600) // 60
        
        # Определяем тип задания
        if 'reminder' in job.id:
            job_type = "💊 Напоминание"
        elif 'content' in job.id:
            job_type = "💝 Контент"
        else:
            job_type = "⚙️ Система"
        
        job_info += f"{i}. **{job_type}**\n"
        job_info += f"   🕐 Время: {next_run.strftime('%H:%M:%S')}\n"
        job_info += f"   📅 Дата: {next_run.strftime('%d.%m.%Y')}\n"
        job_info += f"   ⏳ Через: {int(hours_until)}ч {int(minutes_until)}м\n"
        job_info += f"   🆔 ID: {job.id}\n\n"
    
    job_info += f"🕐 Текущее время: {now.strftime('%H:%M:%S %d.%m.%Y')}"
    
    safe_send_message(message.chat.id, job_info)

@bot.message_handler(commands=['test'])
def test_content(message):
    """Тестовая отправка контента"""
    send_random_content()
    safe_send_message(message.chat.id, "Тестовый контент отправлен! 🌸")

# ------------------- запуск -------------------
def run_bot():
    """Запуск бота с обработкой ошибок"""
    scheduler.start()
    logger.info("Планировщик запущен")
    
    while True:
        try:
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            logger.error(f"Ошибка бота: {e}, перезапуск через 10 секунд...")
            time.sleep(10)

if __name__ == "__main__":
    run_bot()