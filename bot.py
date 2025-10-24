import os
import time
import requests
import json
from threading import Thread, Lock
from flask import Flask
import telebot
from telebot import types
import logging

print("🚀 AutoQiyos Bot запускается...")

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    logger.error("❌ BOT_TOKEN не найден в переменных окружения!")
    exit(1)

bot = telebot.TeleBot(TOKEN, parse_mode='HTML')

# Удаляем webhook
try:
    bot.delete_webhook(drop_pending_updates=True)
    time.sleep(1)
    logger.info("✅ Webhook удален")
except Exception as e:
    logger.warning(f"⚠️ Ошибка при удалении webhook: {e}")

# УЛУЧШЕННЫЙ КЛАСС ДЛЯ РАБОТЫ С БАЗОЙ ДАННЫХ
class CarDatabase:
    def __init__(self):
        self.db_url = "https://raw.githubusercontent.com/Behzod1988/autoqiyos-bot/main/car_database.json"
        self.data = None
        self.last_update = 0
        self.update_interval = 3600  # 1 час
        self.lock = Lock()
        self.load_database()
        
        # Запускаем фоновое обновление
        self.update_thread = Thread(target=self.periodic_update, daemon=True)
        self.update_thread.start()
    
    def periodic_update(self):
        """Фоновое обновление базы данных"""
        while True:
            time.sleep(self.update_interval)
            try:
                self.load_database()
            except Exception as e:
                logger.error(f"❌ Ошибка фонового обновления: {e}")
    
    def load_database(self):
        """Загрузка базы данных с блокировкой"""
        try:
            with self.lock:
                response = requests.get(self.db_url, timeout=15)
                response.raise_for_status()
                self.data = response.json()
                self.last_update = time.time()
                logger.info(f"✅ База обновлена: {len(self.data['cars'])} автомобилей")
                return True
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки базы: {e}")
            return False
    
    def find_car(self, car_name):
        """Умный поиск автомобиля"""
        if not self.data:
            if not self.load_database():
                return None
        
        car_name_lower = car_name.lower().strip()
        found_cars = []
        
        # Поиск по точному совпадению
        for car_key in self.data["cars"]:
            if car_name_lower == car_key.lower():
                return self.data["cars"][car_key]
        
        # Поиск по частичному совпадению (с оценкой релевантности)
        for car_key in self.data["cars"]:
            key_lower = car_key.lower()
            if (car_name_lower in key_lower or 
                key_lower in car_name_lower or
                any(word in key_lower for word in car_name_lower.split())):
                found_cars.append((car_key, self.data["cars"][car_key]))
        
        # Возвращаем самый релевантный результат
        if found_cars:
            # Сортируем по длине названия (более короткие обычно точнее)
            found_cars.sort(key=lambda x: len(x[0]))
            return found_cars[0][1]
        
        return None
    
    def get_all_brands(self):
        """Получить все марки автомобилей"""
        if not self.data:
            return []
        return list(self.data["cars"].keys())
    
    def force_update(self):
        """Принудительное обновление базы"""
        return self.load_database()

# Инициализируем базу
car_db = CarDatabase()

# Flask app для Railway
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 AutoQiyos Bot с улучшенной базой данных работает!"

@app.route('/health')
def health():
    return {"status": "healthy", "cars_loaded": len(car_db.data["cars"]) if car_db.data else 0}

@app.route('/update-db')
def update_db():
    """Эндпоинт для принудительного обновления базы"""
    if car_db.force_update():
        return {"status": "success", "cars_count": len(car_db.data["cars"])}
    return {"status": "error"}, 500

def run_flask():
    app.run(host='0.0.0.0', port=8080, debug=False)

Thread(target=run_flask, daemon=True).start()

# УЛУЧШЕННЫЕ КЛАВИАТУРЫ
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🚗 Сравнить авто", "🔎 Найти авто")
    markup.add("📊 Все марки", "🔄 Обновить базу")
    markup.add("ℹ️ О проекте", "💬 Поддержка")
    return markup

def back_button():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("⬅️ Назад в меню")
    return markup

def brands_keyboard():
    """Клавиатура с популярными марками"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    popular_brands = ["Chevrolet", "Toyota", "Hyundai", "Kia", "Nexia", "Gentra", "Cobalt", "Tracker", "Onix"]
    for brand in popular_brands:
        markup.add(brand)
    markup.add("⬅️ Назад в меню")
    return markup

# ОБРАБОТЧИКИ КОМАНД
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🚘 <b>AutoQiyos — сравни авто легко!</b>\n\n"
        "Я помогу сравнить характеристики и цены автомобилей. Выбери действие:",
        reply_markup=main_menu()
    )

@bot.message_handler(commands=['update'])
def update_command(message):
    """Команда для обновления базы"""
    msg = bot.send_message(message.chat.id, "🔄 Обновляю базу данных...")
    if car_db.force_update():
        bot.edit_message_text(
            f"✅ База обновлена!\n📊 Автомобилей: {len(car_db.data['cars'])}",
            message.chat.id,
            msg.message_id
        )
    else:
        bot.edit_message_text(
            "❌ Не удалось обновить базу. Попробуйте позже.",
            message.chat.id,
            msg.message_id
        )

@bot.message_handler(func=lambda message: message.text == "🚗 Сравнить авто")
def start_comparison(message):
    bot.send_message(
        message.chat.id,
        "🔧 Введите два автомобиля для сравнения:\n\n"
        "<b>Формат:</b>\n"
        "<code>Onix vs Tracker</code>\n"
        "Или\n"
        "<code>Onix против Tracker</code>\n\n"
        "Можно использовать кнопки ниже для быстрого выбора:",
        parse_mode='HTML',
        reply_markup=brands_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == "🔎 Найти авто")
def search_car(message):
    bot.send_message(
        message.chat.id,
        "🔍 Введите название автомобиля для поиска:\n\n"
        "Например: <code>Cobalt</code>, <code>Nexia 3</code>",
        parse_mode='HTML',
        reply_markup=brands_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == "📊 Все марки")
def show_all_brands(message):
    brands = car_db.get_all_brands()
    if brands:
        # Разбиваем на части для избежания ограничения длины
        brands_text = "\n".join(sorted(brands)[:50])  # Показываем первые 50
        text = f"📊 Доступные марки ({len(brands)}):\n\n{brands_text}"
        if len(brands) > 50:
            text += f"\n\n... и еще {len(brands) - 50} автомобилей"
    else:
        text = "❌ База данных пуста или не загружена"
    
    bot.send_message(message.chat.id, text, reply_markup=back_button())

@bot.message_handler(func=lambda message: message.text == "🔄 Обновить базу")
def update_db_handler(message):
    update_command(message)

@bot.message_handler(func=lambda message: message.text == "ℹ️ О проекте")
def about_project(message):
    bot.send_message(
        message.chat.id,
        "ℹ️ <b>AutoQiyos</b> — умный бот для сравнения автомобилей!\n\n"
        "📊 <b>Возможности:</b>\n"
        "• Сравнение характеристик\n"
        "• Актуальные цены\n"
        "• Расход топлива\n"
        "• Технические параметры\n\n"
        "🔄 База данных автоматически обновляется",
        parse_mode='HTML',
        reply_markup=back_button()
    )

@bot.message_handler(func=lambda message: message.text == "💬 Поддержка")
def contact_admin(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📞 Написать разработчику", url="https://t.me/behzod_islomoff"))
    markup.add(types.InlineKeyboardButton("🐛 Сообщить об ошибке", url="https://github.com/Behzod1988/autoqiyos-bot/issues"))
    bot.send_message(
        message.chat.id,
        "📞 <b>Поддержка</b>\n\n"
        "По всем вопросам и предложениям:",
        parse_mode='HTML',
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "⬅️ Назад в меню")
def back_to_menu(message):
    bot.send_message(message.chat.id, "🏠 Главное меню:", reply_markup=main_menu())

# УЛУЧШЕННЫЙ ОБРАБОТЧИК СРАВНЕНИЯ
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    text = message.text.strip()
    
    # Проверяем на сравнение
    if " vs " in text.lower() or " против " in text.lower():
        handle_comparison(message, text)
    else:
        # Поиск одного автомобиля
        handle_single_car(message, text)

def handle_comparison(message, text):
    """Обработка сравнения двух автомобилей"""
    try:
        # Определяем разделитель
        if " vs " in text.lower():
            car1, car2 = text.split(" vs ", 1)
            separator = "vs"
        else:
            car1, car2 = text.split(" против ", 1)
            separator = "против"
        
        car1 = car1.strip()
        car2 = car2.strip()
        
        logger.info(f"🔍 Сравниваем: '{car1}' {separator} '{car2}'")
        
        info1 = car_db.find_car(car1)
        info2 = car_db.find_car(car2)
        
        response = format_comparison_response(car1, car2, info1, info2)
        bot.send_message(message.chat.id, response, parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"Ошибка сравнения: {e}")
        bot.send_message(
            message.chat.id,
            "❌ Ошибка при сравнении. Используйте формат: 'Onix vs Tracker'",
            reply_markup=brands_keyboard()
        )

def format_comparison_response(car1, car2, info1, info2):
    """Форматирование ответа для сравнения"""
    if info1 and info2:
        response = f"🔄 <b>Сравнение автомобилей:</b>\n\n"
        
        # Сравниваем цены
        price1 = int(info1['price'].replace('$', '').replace(' ', ''))
        price2 = int(info2['price'].replace('$', '').replace(' ', ''))
        price_diff = price1 - price2
        
        response += f"🚗 <b>{car1}</b>:\n"
        response += f"💰 Цена: {info1['price']}"
        if price_diff != 0:
            response += f" ({'+' if price_diff > 0 else ''}{price_diff}$)"
        response += f"\n⚙️ Двигатель: {info1['engine']}\n"
        response += f"⛽ Расход: {info1['fuel']} л/100km\n"
        response += f"📊 КПП: {info1['transmission']}\n"
        response += f"🎯 Тип: {info1['type']}\n\n"
        
        response += f"🚙 <b>{car2}</b>:\n" 
        response += f"💰 Цена: {info2['price']}"
        if price_diff != 0:
            response += f" ({'-' if price_diff > 0 else '+'}{abs(price_diff)}$)"
        response += f"\n⚙️ Двигатель: {info2['engine']}\n"
        response += f"⛽ Расход: {info2['fuel']} л/100km\n"
        response += f"📊 КПП: {info2['transmission']}\n"
        response += f"🎯 Тип: {info2['type']}\n\n"
        
        # Вывод победителя по цене
        if price_diff > 0:
            response += f"🏆 <b>По цене выгоднее: {car2}</b>\n\n"
        elif price_diff < 0:
            response += f"🏆 <b>По цене выгоднее: {car1}</b>\n\n"
        else:
            response += f"💰 <b>Цены одинаковые</b>\n\n"
        
        response += f"📅 <i>Данные актуальны на: {car_db.data.get('last_updated', 'N/A')}</i>"
        
    elif info1:
        response = format_single_car_response(car1, info1)
        response += f"\n\n❌ Автомобиль '{car2}' не найден в базе"
    elif info2:
        response = format_single_car_response(car2, info2)
        response += f"\n\n❌ Автомобиль '{car1}' не найден в базе"
    else:
        response = "❌ Оба автомобиля не найдены в базе данных\n\n"
        response += "Попробуйте использовать кнопки ниже:"
    
    return response

def handle_single_car(message, text):
    """Обработка поиска одного автомобиля"""
    car_info = car_db.find_car(text)
    if car_info:
        response = format_single_car_response(text, car_info)
        bot.send_message(message.chat.id, response, parse_mode='HTML')
    else:
        bot.send_message(
            message.chat.id,
            f"❌ Автомобиль '{text}' не найден.\n\n"
            "Попробуйте:\n"
            "• Проверить написание\n"
            "• Использовать кнопки ниже\n"
            "• Или сравнить два авто: 'Onix vs Tracker'",
            reply_markup=brands_keyboard()
        )

def format_single_car_response(car_name, car_info):
    """Форматирование ответа для одного автомобиля"""
    response = f"🚗 <b>{car_name}</b>\n\n"
    response += f"💰 Цена: {car_info['price']}\n"
    response += f"⚙️ Двигатель: {car_info['engine']}\n"
    response += f"⛽ Расход: {car_info['fuel']} л/100km\n"
    response += f"📊 КПП: {car_info['transmission']}\n"
    response += f"🎯 Тип: {car_info['type']}\n"
    response += f"📅 Годы: {car_info['years']}\n\n"
    
    if 'features' in car_info and car_info['features']:
        features = car_info['features']
        if len(features) > 5:
            response += f"🔧 Основные опции: {', '.join(features[:5])}...\n"
        else:
            response += f"🔧 Опции: {', '.join(features)}\n"
    
    response += f"\n📅 Актуально на: {car_db.data.get('last_updated', 'N/A')}"
    
    return response

logger.info("✅ Бот с улучшенной базой данных запущен!")
try:
    bot.infinity_polling(timeout=60, long_polling_timeout=30)
except Exception as e:
    logger.error(f"❌ Ошибка запуска бота: {e}")
