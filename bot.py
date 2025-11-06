import telebot
import random
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import os
import logging
import requests
from zoneinfo import ZoneInfo  # 🔴 ВСТРОЕННАЯ БИБЛИОТЕКА (Python 3.9+)

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

# 🔴 УКАЗЫВАЕМ МОСКОВСКИЙ ЧАСОВОЙ ПОЯС (встроенными средствами)
try:
    MOSCOW_TZ = ZoneInfo("Europe/Moscow")
except:
    # Если zoneinfo не доступен, используем UTC+3
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
def get_moscow_time():
    """🔴 ПОЛУЧАЕМ ТЕКУЩЕЕ ВРЕМЯ В МОСКВЕ"""
    if MOSCOW_TZ:
        return datetime.now(MOSCOW_TZ)
    else:
        # Если нет zoneinfo, используем UTC+3 вручную
        return datetime.utcnow() + timedelta(hours=3)

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
            last_message_time = get_moscow_time()
        except Exception as e:
            logger.error(f"Ошибка отправки напоминания: {e}")

def send_random_sweet_message(ignore_interval=False):
    global last_message_time
    now = get_moscow_time()
    if not ignore_interval and last_message_time and (now - last_message_time) < MIN_INTERVAL:
        return
    if user_chat_id:
        logger.info("Отправка милого сообщения")
        try:
            bot.send_message(user_chat_id, random.choice(sweet_messages))
            last_message_time = now
        except Exception as e:
            logger.error(f"Ошибка отправки милого сообщения: {e}")

def send_random_meme(ignore_interval=False):
    global last_message_time
    now = get_moscow_time()
    if not ignore_interval and last_message_time and (now - last_message_time) < MIN_INTERVAL:
        return
    if user_chat_id:
        logger.info("Отправка мема")
        try:
            bot.send_photo(user_chat_id, random.choice(memes))
            last_message_time = now
        except Exception as e:
            logger.error(f"Ошибка отправки мема: {e}")
            try:
                bot.send_message(user_chat_id, "📸 не получилось отправить мем, но вот мысленный мем для тебя! 😊")
            except Exception as e2:
                logger.error(f"Ошибка отправки запасного сообщения: {e2}")

def welcome_keyboard():
    """Клавиатура для приветственного сообщения"""
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("💚 уже принял", callback_data="already_taken"),
        telebot.types.InlineKeyboardButton("🤔 еще нет", callback_data="not_yet")
    )
    return markup

def reminder_keyboard():
    """Клавиатура для обычного напоминания"""
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("💚 принял", callback_data="taken"),
        telebot.types.InlineKeyboardButton("🕒 отложить на час", callback_data="delay")
    )
    return markup

def remove_reminder_jobs():
    """Удаляем только задания напоминаний"""
    for job_id in ["interval_reminder", "delayed_reminder", "first_reminder", "restart_intervals_after_delay"]:
        try:
            scheduler.remove_job(job_id)
        except:
            pass

def schedule_interval_reminders(start_delay_minutes=0):
    """Планируем регулярные интервальные напоминания"""
    remove_reminder_jobs()
    
    now = get_moscow_time()  # 🔴 ИСПОЛЬЗУЕМ МОСКОВСКОЕ ВРЕМЯ
    
    if start_delay_minutes > 0:
        # Если указана задержка
        start_time = now + timedelta(minutes=start_delay_minutes)
    else:
        # Определяем время первого напоминания
        if now.hour >= 8:
            # Если уже после 8 утра - начинаем через 30 минут
            start_time = now + timedelta(minutes=30)
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

def schedule_first_reminder():
    """Планируем первое напоминание через 30 минут"""
    remove_reminder_jobs()
    
    run_time = get_moscow_time() + timedelta(minutes=30)  # 🔴 МОСКОВСКОЕ ВРЕМЯ
    
    scheduler.add_job(
        send_reminder,
        'date',
        run_date=run_time,
        id="first_reminder"
    )
    
    # После первого напоминания запускаем интервальные
    scheduler.add_job(
        schedule_interval_reminders,
        'date',
        run_date=run_time + timedelta(minutes=5),
        kwargs={'start_delay_minutes': 0},
        id="start_interval_after_first"
    )
    
    logger.info(f"Первое напоминание запланировано на {run_time}")

def schedule_delayed_reminder():
    """Планируем одно отложенное напоминание и затем снова интервальные"""
    remove_reminder_jobs()
    
    # Отложенное напоминание через час
    run_time = get_moscow_time() + timedelta(hours=1)  # 🔴 МОСКОВСКОЕ ВРЕМЯ
    
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
    
    now = get_moscow_time()  # 🔴 МОСКОВСКОЕ ВРЕМЯ
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
        logger.info(f"Запланировано милое сообщение {i+1} на {run_time}")
    
    # Планируем 2 мема в случайное время с 10 до 22
    for i in range(2):
        hour = random.randint(10, 22)
        minute = random.randint(0, 59)
        run_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Если время уже прошло сегодня, планируем на завтра
        if run_time < now:
            run_time += timedelta(days=1)
        
        scheduler.add_job(
            send_random_meme, 
            'date', 
            run_date=run_time,
            id=f"meme_{i}"
        )
        logger.info(f"Запланирован мем {i+1} на {run_time}")

# ------------------- обработчики -------------------
@bot.message_handler(commands=['start'])
def start(message):
    global user_chat_id
    user_chat_id = message.chat.id
    logger.info(f"Бот запущен пользователем {user_chat_id}")
    
    # Определяем какое сообщение показать в зависимости от времени
    now = get_moscow_time()  # 🔴 МОСКОВСКОЕ ВРЕМЯ
    if now.hour >= 8:
        greeting = "привет, солнышко ☀️ я буду напоминать тебе о таблетках каждые 30 минут 💊\n\nты уже выпил сегодняшнюю таблетку?"
    else:
        greeting = "привет, солнышко ☀️ я буду напоминать тебе о таблетках каждые 30 минут с 8 утра 💊\n\nты уже выпил таблетку?"
    
    bot.send_message(user_chat_id, greeting, reply_markup=welcome_keyboard())
    
    # Пока не планируем напоминания - ждем ответ пользователя
    schedule_content_messages()

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    logger.info(f"Обработка callback: {call.data}")
    
    if call.data == "already_taken":
        bot.answer_callback_query(call.id, "умничка! 🌸 напоминания вернутся завтра 💖")
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None
        )
        # Переносим напоминания на завтра в 8 утра
        schedule_interval_reminders(start_delay_minutes=24*60)
        bot.send_message(user_chat_id, "отлично! 💚 напоминания возобновятся завтра с 8 утра 🌞")
        bot.send_message(OWNER_CHAT_ID, f"сашенька отметил, что выпил таблетку 💊")

    elif call.data == "not_yet":
        bot.answer_callback_query(call.id, "хорошо, напомню через полчаса 💕")
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None
        )
        # Планируем первое напоминание через 30 минут
        schedule_first_reminder()
        bot.send_message(user_chat_id, "хорошо 😽 напомню тебе про таблетку через полчаса! 🌸")

    elif call.data == "taken":
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

# ------------------- команды для управления -------------------
@bot.message_handler(commands=['test_meme'])
def test_meme(message):
    """Принудительная отправка мема для тестирования"""
    send_random_meme(ignore_interval=True)

@bot.message_handler(commands=['test_message'])
def test_message(message):
    """Принудительная отправка милого сообщения для тестирования"""
    send_random_sweet_message(ignore_interval=True)

@bot.message_handler(commands=['test_reminder'])
def test_reminder(message):
    """Принудительная отправка напоминания для тестирования"""
    send_reminder()

@bot.message_handler(commands=['jobs'])
def show_jobs(message):
    """Показать активные задания"""
    jobs = scheduler.get_jobs()
    job_info = "Активные задания:\n\n"
    for job in jobs:
        job_info += f"• {job.id} - {job.next_run_time}\n"
    bot.send_message(message.chat.id, job_info)
    logger.info(f"Пользователю отправлена информация о {len(jobs)} заданиях")

@bot.message_handler(commands=['restart'])
def restart_bot(message):
    """Перезапустить планировщик"""
    scheduler.remove_all_jobs()
    schedule_content_messages()
    bot.send_message(message.chat.id, "Планировщик перезапущен! 🌸")
    # Перезапускаем с приветственным сообщением
    start(message)

@bot.message_handler(commands=['debug'])
def debug_info(message):
    """Отладочная информация"""
    global user_chat_id, last_message_time
    now = get_moscow_time()
    timezone_info = "Europe/Moscow (ZoneInfo)" if MOSCOW_TZ else "UTC+3 (ручная коррекция)"
    
    debug_text = f"""
🔧 Отладочная информация:
• User ID: {user_chat_id}
• Текущее время (МСК): {now}
• Последнее сообщение: {last_message_time}
• Активных заданий: {len(scheduler.get_jobs())}
• Владелец: {OWNER_CHAT_ID}
• Часовой пояс: {timezone_info}
    """
    bot.send_message(message.chat.id, debug_text)

@bot.message_handler(commands=['clear_jobs'])
def clear_jobs(message):
    """Очистить все задания"""
    scheduler.remove_all_jobs()
    bot.send_message(message.chat.id, "Все задания очищены! 🧹")

@bot.message_handler(commands=['status'])
def status(message):
    """Текущий статус бота"""
    jobs = scheduler.get_jobs()
    reminder_jobs = [job for job in jobs if 'reminder' in job.id]
    content_jobs = [job for job in jobs if 'message' in job.id or 'meme' in job.id]
    
    status_text = f"""
📊 Статус бота:
• Напоминания: {len(reminder_jobs)} заданий
• Контент: {len(content_jobs)} заданий
• Всего: {len(jobs)} заданий
• Пользователь: {'подключен' if user_chat_id else 'не подключен'}
• Время МСК: {get_moscow_time().strftime('%H:%M:%S')}
    """
    bot.send_message(message.chat.id, status_text)

@bot.message_handler(commands=['time'])
def show_time(message):
    """Показать текущее московское время"""
    now = get_moscow_time()
    bot.send_message(message.chat.id, f"🕐 Текущее время в Москве: {now.strftime('%H:%M:%S %d.%m.%Y')}")

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

# ------------------- старт -------------------
if __name__ == "__main__":
    scheduler.start()
    logger.info("Планировщик запущен с московским часовым поясом")
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logger.error(f"Ошибка в боте: {e}")