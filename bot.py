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
    # ... остальные сообщения
]

memes = [
    "https://i.yapx.ru/cEGTF.jpg",
    "https://i.yapx.ru/cEGTH.jpg",
    # ... остальные мемы
]

last_message_time = None
MIN_INTERVAL = timedelta(minutes=20)

# ------------------- функции -------------------
def send_reminder():
    global last_message_time
    if user_chat_id:
        logger.info("Отправка напоминания о таблетке")
        try:
            bot.send_message(
                user_chat_id,
                "💊 пора принять таблетку!\n\nнажми «принял 💚» если уже выпил, или «отложить на час 🕒» если позже 💕",
                reply_markup=reminder_keyboard()
            )
            last_message_time = datetime.now()
        except Exception as e:
            logger.error(f"Ошибка отправки напоминания: {e}")

def send_random_sweet_message():
    global last_message_time
    now = datetime.now()
    if last_message_time and (now - last_message_time) < MIN_INTERVAL:
        return
    if user_chat_id:
        logger.info("Отправка милого сообщения")
        try:
            message = random.choice(sweet_messages)
            bot.send_message(user_chat_id, message)
            last_message_time = now
        except Exception as e:
            logger.error(f"Ошибка отправки милого сообщения: {e}")

def send_random_meme():
    global last_message_time
    now = datetime.now()
    if last_message_time and (now - last_message_time) < MIN_INTERVAL:
        return
    if user_chat_id:
        logger.info("Отправка мема")
        try:
            meme_url = random.choice(memes)
            bot.send_photo(user_chat_id, meme_url)
            last_message_time = now
        except Exception as e:
            logger.error(f"Ошибка отправки мема: {e}")

def reminder_keyboard():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("💚 принял", callback_data="taken"),
        telebot.types.InlineKeyboardButton("🕒 отложить на час", callback_data="delay")
    )
    return markup

def remove_reminder_jobs():
    """Удаляем только задания напоминаний"""
    for job_id in ["interval_reminder", "delayed_reminder", "first_reminder_today", "restart_intervals_after_delay"]:
        try:
            scheduler.remove_job(job_id)
        except:
            pass

def schedule_interval_reminders(start_delay_minutes=0):
    """Планируем регулярные интервальные напоминания"""
    remove_reminder_jobs()
    
    now = datetime.now()
    
    if start_delay_minutes > 0:
        # Если указана задержка (например, после "принял")
        start_time = now + timedelta(minutes=start_delay_minutes)
    else:
        # Определяем время первого напоминания
        if now.hour >= 8:
            # Если уже после 8 утра - начинаем СЕЙЧАС
            start_time = now
        else:
            # Если до 8 утра - начинаем в 8:00
            start_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
    
    logger.info(f"Планируем интервальные напоминания с {start_time}")
    
    scheduler.add_job(
        send_reminder, 
        'interval', 
        minutes=30,
        start_date=start_time,
        id="interval_reminder"
    )
    
    # 🔴 ВАЖНО: если первый запуск после 8 утра, отправляем напоминание сразу
    if start_delay_minutes == 0 and now.hour >= 8:
        # Запланируем первое напоминание через 10 секунд
        scheduler.add_job(
            send_reminder,
            'date',
            run_date=now + timedelta(seconds=10),
            id="first_reminder_today"
        )
        logger.info("Добавлено первое напоминание сегодня")

def schedule_delayed_reminder():
    """Планируем одно отложенное напоминание и затем снова интервальные"""
    remove_reminder_jobs()
    
    # Отложенное напоминание через час
    run_time = datetime.now() + timedelta(hours=1)
    scheduler.add_job(
        send_reminder, 
        'date', 
        run_date=run_time, 
        id="delayed_reminder"
    )
    
    # После отложенного напоминания снова запускаем интервальные
    scheduler.add_job(
        schedule_interval_reminders,
        'date',
        run_date=run_time + timedelta(minutes=5),
        kwargs={'start_delay_minutes': 0},
        id="restart_intervals_after_delay"
    )
    
    logger.info(f"Отложенное напоминание на {run_time}, затем интервальные")

def schedule_content_messages():
    """Планируем мемы и милые сообщения на день"""
    # Удаляем старые задания контента
    for i in range(10):
        for content_type in ['sweet_message', 'meme']:
            try:
                scheduler.remove_job(f"{content_type}_{i}")
            except:
                pass
    
    now = datetime.now()
    logger.info(f"Планирование контента на день")
    
    # Планируем 3 милых сообщения в случайное время с 9 до 22
    for i in range(3):
        hour = random.randint(9, 22)
        minute = random.randint(0, 59)
        run_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Если время уже прошло сегодня, планируем на завтра
        if run_time < now:
            run_time += timedelta(days=1)
        
        scheduler.add_job(
            send_random_sweet_message, 
            'date', 
            run_date=run_time,
            id=f"sweet_message_{i}"
        )
    
    # Планируем 2 мема в случайное время с 10 до 22
    for i in range(2):
        hour = random.randint(10, 22)
        minute = random.randint(0, 59)
        run_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        if run_time < now:
            run_time += timedelta(days=1)
        
        scheduler.add_job(
            send_random_meme, 
            'date', 
            run_date=run_time,
            id=f"meme_{i}"
        )

# ------------------- обработчики -------------------
@bot.message_handler(commands=['start'])
def start(message):
    global user_chat_id
    user_chat_id = message.chat.id
    logger.info(f"Бот запущен пользователем {user_chat_id}")
    
    # Определяем какое сообщение показать в зависимости от времени
    now = datetime.now()
    if now.hour >= 8:
        greeting = "привет, солнышко ☀️ я буду напоминать тебе о таблетках каждые 30 минут начиная с сегодняшнего дня 💊\n\nты уже выпил сегодняшнюю таблетку?"
    else:
        greeting = "привет, солнышко ☀️ я буду напоминать тебе о таблетках каждые 30 минут с 8 утра 💊\n\nты уже выпил таблетку?"
    
    bot.send_message(user_chat_id, greeting, reply_markup=reminder_keyboard())
    
    schedule_interval_reminders()
    schedule_content_messages()

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    logger.info(f"Обработка callback: {call.data}")
    
    if call.data == "taken":
        bot.answer_callback_query(call.id, "умничка! 🌸 напоминания вернутся завтра 💖")
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None
        )
        # Переносим напоминания на завтра в 8 утра
        schedule_interval_reminders(start_delay_minutes=24*60)
        bot.send_message(OWNER_CHAT_ID, f"сашенька отметил, что выпил таблетку 💊")

    elif call.data == "delay":
        bot.answer_callback_query(call.id, "окей, напомню через час 💕")
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None
        )
        schedule_delayed_reminder()

# ------------------- остальные функции без изменений -------------------
# ... (команды для управления, эхо-функция и т.д.)

if __name__ == "__main__":
    scheduler.start()
    logger.info("Планировщик запущен")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logger.error(f"Ошибка в боте: {e}")