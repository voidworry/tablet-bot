import telebot
import random
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import os
import logging
import requests
from zoneinfo import ZoneInfo
import threading
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
print("token и owner_chat_id загружены успешно.")

try:
    MOSCOW_TZ = ZoneInfo("Europe/Moscow")
except:
    logger.warning("ZoneInfo не доступен, используем UTC+3")
    MOSCOW_TZ = None

# 🔴 ОПТИМИЗАЦИЯ: настройка бота с таймаутами
bot = telebot.TeleBot(TOKEN, threaded=True, num_threads=4)
scheduler = BackgroundScheduler(timezone=MOSCOW_TZ) if MOSCOW_TZ else BackgroundScheduler()
user_chat_id = None

# 🔴 ОПТИМИЗАЦИЯ: кэш для быстрого доступа к контенту
class ContentCache:
    def __init__(self):
        self.sweet_messages = [
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
        self.memes = [
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
            "https://i.yapx.ru/cEGTa.jpg",
            "https://i.yapx.ru/cEPww.jpg",
            "https://i.yapx.ru/cEPwz.jpg",
            "https://i.yapx.ru/cEPw5.jpg",
            "https://i.yapx.ru/cEPw8.jpg",
            "https://i.yapx.ru/cEPyA.jpg",
            "https://i.yapx.ru/cEPyC.jpg",
            "https://i.yapx.ru/cEPyE.jpg",
            "https://i.yapx.ru/cEPyH.jpg",
            "https://i.yapx.ru/cEPyO.jpg",
            "https://i.yapx.ru/cEPyR.jpg",
            "https://i.yapx.ru/cEPyT.jpg",
            "https://i.yapx.ru/cEPyU.jpg",
            "https://i.yapx.ru/cEPyW.jpg",
            "https://i.yapx.ru/cEPyY.jpg",
            "https://i.yapx.ru/cEPyZ.jpg",
            "https://i.yapx.ru/cEPyc.jpg",
            "https://i.yapx.ru/cEPyd.jpg",
            "https://i.yapx.ru/cEPyf.jpg",
            "https://i.yapx.ru/cEPyi.jpg",
            "https://i.yapx.ru/cEPyn.jpg",
            "https://i.yapx.ru/cEPyw.jpg",
            "https://i.yapx.ru/cEPyy.jpg",
            "https://i.yapx.ru/cEPyz.jpg",
            "https://i.yapx.ru/cEPy1.jpg",
            "https://i.yapx.ru/cEPy4.jpg",
            "https://i.yapx.ru/cEPy6.jpg"
        ]
        self._last_meme_index = -1
        self._last_message_index = -1
    
    def get_random_sweet_message(self):
        """🔴 ОПТИМИЗАЦИЯ: избегаем повторений подряд"""
        if len(self.sweet_messages) <= 1:
            return random.choice(self.sweet_messages)
        
        index = random.randint(0, len(self.sweet_messages) - 1)
        while index == self._last_message_index:
            index = random.randint(0, len(self.sweet_messages) - 1)
        
        self._last_message_index = index
        return self.sweet_messages[index]
    
    def get_random_meme(self):
        """🔴 ОПТИМИЗАЦИЯ: избегаем повторений подряд"""
        if len(self.memes) <= 1:
            return random.choice(self.memes)
        
        index = random.randint(0, len(self.memes) - 1)
        while index == self._last_meme_index:
            index = random.randint(0, len(self.memes) - 1)
        
        self._last_meme_index = index
        return self.memes[index]

# 🔴 ОПТИМИЗАЦИЯ: создаем кэш
content_cache = ContentCache()

last_message_time = None
MIN_INTERVAL = timedelta(minutes=20)

# 🔴 ОПТИМИЗАЦИЯ: кэш для клавиатур
_keyboard_cache = {}

def get_welcome_keyboard():
    """🔴 ОПТИМИЗАЦИЯ: кэшируем клавиатуры"""
    if 'welcome' not in _keyboard_cache:
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("💚 уже принял", callback_data="already_taken"),
            telebot.types.InlineKeyboardButton("🤔 еще нет", callback_data="not_yet")
        )
        _keyboard_cache['welcome'] = markup
    return _keyboard_cache['welcome']

def get_reminder_keyboard():
    """🔴 ОПТИМИЗАЦИЯ: кэшируем клавиатуры"""
    if 'reminder' not in _keyboard_cache:
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("💚 принял", callback_data="taken"),
            telebot.types.InlineKeyboardButton("🕒 отложить на час", callback_data="delay")
        )
        _keyboard_cache['reminder'] = markup
    return _keyboard_cache['reminder']

# ------------------- оптимизированные функции -------------------
def get_moscow_time():
    """🔴 ОПТИМИЗАЦИЯ: быстрая функция времени"""
    if MOSCOW_TZ:
        return datetime.now(MOSCOW_TZ)
    else:
        return datetime.utcnow() + timedelta(hours=3)

def send_reminder():
    global last_message_time
    if user_chat_id:
        logger.info("Отправка напоминания о таблетке")
        try:
            # 🔴 ОПТИМИЗАЦИЯ: быстрая отправка без повторного создания клавиатуры
            bot.send_message(
                user_chat_id,
                "💊 пора принять таблетку!\n\nнажми «принял 💚» если уже выпил, или «отложить на час 🕒» если позже 💕",
                reply_markup=get_reminder_keyboard()
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
            # 🔴 ОПТИМИЗАЦИЯ: используем кэш
            message = content_cache.get_random_sweet_message()
            bot.send_message(user_chat_id, message)
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
            # 🔴 ОПТИМИЗАЦИЯ: используем кэш и быстрый выбор
            meme_url = content_cache.get_random_meme()
            
            # 🔴 ОПТИМИЗАЦИЯ: отправляем фото без предварительной проверки (Telegram сам проверит)
            bot.send_photo(user_chat_id, meme_url)
            last_message_time = now
            
        except Exception as e:
            logger.error(f"Ошибка отправки мема: {e}")
            try:
                bot.send_message(user_chat_id, "📸 не получилось отправить мем, но вот мысленный мем для тебя! 😊")
            except Exception as e2:
                logger.error(f"Ошибка отправки запасного сообщения: {e2}")

def remove_reminder_jobs():
    """🔴 ОПТИМИЗАЦИЯ: быстрая очистка заданий"""
    job_ids = ["interval_reminder", "delayed_reminder", "first_reminder", "restart_intervals_after_delay"]
    for job_id in job_ids:
        try:
            scheduler.remove_job(job_id)
        except:
            pass

def schedule_interval_reminders(start_delay_minutes=0):
    """🔴 ОПТИМИЗАЦИЯ: оптимизированное планирование"""
    remove_reminder_jobs()
    
    now = get_moscow_time()
    
    if start_delay_minutes > 0:
        start_time = now + timedelta(minutes=start_delay_minutes)
    else:
        if now.hour >= 8:
            start_time = now + timedelta(minutes=30)
        else:
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
    remove_reminder_jobs()
    
    run_time = get_moscow_time() + timedelta(minutes=30)
    
    scheduler.add_job(
        send_reminder,
        'date',
        run_date=run_time,
        id="first_reminder"
    )
    
    scheduler.add_job(
        schedule_interval_reminders,
        'date',
        run_date=run_time + timedelta(minutes=5),
        kwargs={'start_delay_minutes': 0},
        id="start_interval_after_first"
    )
    
    logger.info(f"Первое напоминание запланировано на {run_time}")

def schedule_delayed_reminder():
    remove_reminder_jobs()
    
    run_time = get_moscow_time() + timedelta(hours=1)
    
    scheduler.add_job(
        send_reminder, 
        'date', 
        run_date=run_time, 
        id="delayed_reminder"
    )
    
    scheduler.add_job(
        schedule_interval_reminders,
        'date',
        run_date=run_time + timedelta(minutes=5),
        kwargs={'start_delay_minutes': 0},
        id="restart_intervals_after_delay"
    )
    
    logger.info(f"Отложенное напоминание на {run_time}, затем интервальные")

def schedule_content_messages():
    """🔴 ОПТИМИЗАЦИЯ: оптимизированное планирование контента"""
    # Быстрая очистка старых заданий
    for i in range(5):  # 🔴 ОПТИМИЗАЦИЯ: уменьшили диапазон
        for content_type in ['sweet_message', 'meme']:
            try:
                scheduler.remove_job(f"{content_type}_{i}")
            except:
                pass
    
    now = get_moscow_time()
    logger.info(f"🔄 Планирование контента на СЕГОДНЯ: {now.date()}")
    
    today = now.date()
    now_naive = now.replace(tzinfo=None) if now.tzinfo else now
    
    # 🔴 ОПТИМИЗАЦИЯ: предварительно генерируем времена
    message_times = []
    for i in range(3):
        hour = random.randint(9, 22)
        minute = random.randint(0, 59)
        run_time = datetime(today.year, today.month, today.day, hour, minute, 0)
        if run_time > now_naive:
            message_times.append((f"sweet_message_{i}", run_time))
    
    meme_times = []
    for i in range(2):
        hour = random.randint(10, 22)
        minute = random.randint(0, 59)
        run_time = datetime(today.year, today.month, today.day, hour, minute, 0)
        if run_time > now_naive:
            meme_times.append((f"meme_{i}", run_time))
    
    # 🔴 ОПТИМИЗАЦИЯ: массовое добавление заданий
    for job_id, run_time in message_times:
        scheduler.add_job(
            send_random_sweet_message, 
            'date', 
            run_date=run_time,
            id=job_id
        )
        logger.info(f"💝 Запланировано милое сообщение на {run_time}")
    
    for job_id, run_time in meme_times:
        scheduler.add_job(
            send_random_meme, 
            'date', 
            run_date=run_time,
            id=job_id
        )
        logger.info(f"📸 Запланирован мем на {run_time}")
    
    logger.info(f"✅ На сегодня запланировано: {len(message_times)} сообщений, {len(meme_times)} мемов")
    
    # Перепланировка на следующий день
    tomorrow = today + timedelta(days=1)
    next_day_time = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 1, 0)
    
    scheduler.add_job(
        schedule_content_messages,
        'date',
        run_date=next_day_time,
        id="reschedule_content"
    )

# ------------------- обработчики -------------------
@bot.message_handler(commands=['start'])
def start(message):
    global user_chat_id
    user_chat_id = message.chat.id
    logger.info(f"Бот запущен пользователем {user_chat_id}")
    
    now = get_moscow_time()
    if now.hour >= 8:
        greeting = "привет, солнышко ☀️ я буду напоминать тебе о таблетках каждые 30 минут 💊\n\nты уже выпил сегодняшнюю таблетку?"
    else:
        greeting = "привет, солнышко ☀️ я буду напоминать тебе о таблетках каждые 30 минут с 8 утра 💊\n\nты уже выпил таблетку?"
    
    # 🔴 ОПТИМИЗАЦИЯ: быстрая отправка с кэшированной клавиатурой
    bot.send_message(user_chat_id, greeting, reply_markup=get_welcome_keyboard())
    schedule_content_messages()

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    """🔴 ОПТИМИЗАЦИЯ: быстрая обработка callback"""
    logger.info(f"Обработка callback: {call.data}")
    
    # 🔴 ОПТИМИЗАЦИЯ: сразу отвечаем на callback
    try:
        if call.data == "already_taken":
            bot.answer_callback_query(call.id, "умничка! 🌸 напоминания вернутся завтра 💖")
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            schedule_interval_reminders(start_delay_minutes=24*60)
            bot.send_message(call.message.chat.id, "💚 умничка! 🌸 напоминания вернутся завтра в 8 утра 💖")
            bot.send_message(OWNER_CHAT_ID, f"сашенька отметил, что выпил таблетку 💊")

        elif call.data == "not_yet":
            bot.answer_callback_query(call.id, "хорошо, напомню через полчаса 💕")
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            schedule_first_reminder()
            bot.send_message(call.message.chat.id, "💗 хорошо! напомню тебе про таблетку через полчаса! 🌸")

        elif call.data == "taken":
            bot.answer_callback_query(call.id, "умничка! 🌸 напоминания вернутся завтра 💖")
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            schedule_interval_reminders(start_delay_minutes=24*60)
            bot.send_message(call.message.chat.id, "💚 умничка! 🌸 напоминания вернутся завтра в 8 утра 💖")
            bot.send_message(OWNER_CHAT_ID, f"сашенька отметил, что выпил таблетку 💊")

        elif call.data == "delay":
            bot.answer_callback_query(call.id, "окей, напомню через час 💕")
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            bot.send_message(call.message.chat.id, "🕒 окей, напомню через час 💕")
            schedule_delayed_reminder()
            
    except Exception as e:
        logger.error(f"Ошибка в callback: {e}")
        try:
            bot.answer_callback_query(call.id, "⚠️ произошла ошибка")
        except:
            pass

# ... остальные команды без изменений ...

@bot.message_handler(commands=['ping'])
def ping(message):
    """🔴 ОПТИМИЗАЦИЯ: команда для проверки скорости ответа"""
    start_time = time.time()
    bot.send_message(message.chat.id, "🏓 понг!")
    end_time = time.time()
    response_time = round((end_time - start_time) * 1000, 2)
    bot.send_message(message.chat.id, f"⏱ время ответа: {response_time} мс")

# ------------------- старт -------------------
if __name__ == "__main__":
    scheduler.start()
    logger.info("🔴 ОПТИМИЗИРОВАННЫЙ бот запущен")
    try:
        bot.polling(none_stop=True, interval=1, timeout=30)
    except Exception as e:
        logger.error(f"Ошибка в боте: {e}")