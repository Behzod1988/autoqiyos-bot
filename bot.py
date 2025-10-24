import os
import time
import requests
import json
from threading import Thread
from flask import Flask
import telebot
from telebot import types

print("🚀 AutoQiyos Bot запускается...")

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN, parse_mode='HTML')
bot.skip_pending = True  # Фиксим ошибку 409

# Удаляем webhook
try:
    bot.delete_webhook(drop_pending_updates=True)
    time.sleep(2)
except:
    pass

# ПРОСТАЯ БАЗА ДАННЫХ
class CarDatabase:
    def __init__(self):
        self.db_url = "https://raw.githubusercontent.com/Behzod1988/autoqiyos-bot/main/car_database.json"
        self.data = None
        self.load_database()
    
    def load_database(self):
        try:
            response = requests.get(self.db_url, timeout=10)
            self.data = response.json()
            print(f"✅ База загружена: {len(self.data['cars'])} автомобилей")
        except Exception as e:
            print(f"❌ Ошибка загрузки базы: {e}")
            self.data = {"cars": {}}
    
    def find_car(self, car_name):
        if not self.data:
            self.load_database()
        
        car_name_lower = car_name.lower().strip()
        
        # Простой поиск
        for car_key in self.data["cars"]:
            if car_name_lower in car_key.lower():
                return self.data["cars"][car_key]
        
        return None

    def get_price_number(self, price_str):
        """Преобразует цену в число (исправляет ошибку)"""
        try:
            # Убираем $ и пробелы, берем первое число если есть диапазон
            clean = price_str.replace('$', '').replace(' ', '').split('-')[0]
            return int(clean)
        except:
            return 0

# Инициализируем базу
car_db = CarDatabase()

# Flask app для Railway
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 AutoQiyos Bot работает!"

def run_flask():
    app.run(host='0.0.0.0', port=8080, debug=False)

Thread(target=run_flask, daemon=True).start()

# ПРОСТЫЕ КЛАВИАТУРЫ
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚗 Сравнить авто", "🔎 Найти авто")
    markup.add("ℹ️ О проекте", "💬 Поддержка")
    return markup

def back_button():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("⬅️ Назад")
    return markup

# ОСНОВНЫЕ КОМАНДЫ
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🚘 <b>AutoQiyos — сравни авто легко!</b>\n\nВыбери действие:",
        reply_markup=main_menu()
    )

@bot.message_handler(commands=['test'])
def test_command(message):
    """Простая команда для тестирования"""
    bot.send_message(message.chat.id, "✅ Бот работает! Ошибок нет!")

@bot.message_handler(func=lambda message: message.text == "🚗 Сравнить авто")
def compare_cars(message):
    bot.send_message(
        message.chat.id,
        "🔧 Введите два автомобиля:\n\n<b>Формат:</b>\n<code>Onix vs Tracker</code>\nИли\n<code>Onix против Tracker</code>",
        parse_mode='HTML',
        reply_markup=back_button()
    )

@bot.message_handler(func=lambda message: message.text == "🔎 Найти авто")
def find_car(message):
    bot.send_message(
        message.chat.id,
        "🔍 Введите название автомобиля:\n\nНапример: <code>Cobalt</code>",
        parse_mode='HTML',
        reply_markup=back_button()
    )

@bot.message_handler(func=lambda message: message.text == "ℹ️ О проекте")
def about(message):
    bot.send_message(
        message.chat.id,
        "ℹ️ <b>AutoQiyos</b> — бот для сравнения автомобилей!\n\nПростая и удобная версия.",
        parse_mode='HTML',
        reply_markup=back_button()
    )

@bot.message_handler(func=lambda message: message.text == "💬 Поддержка")
def support(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📞 Написать", url="https://t.me/behzod_islomoff"))
    bot.send_message(message.chat.id, "Связь с разработчиком:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "⬅️ Назад")
def back(message):
    bot.send_message(message.chat.id, "Главное меню:", reply_markup=main_menu())

# ОБРАБОТКА ВСЕХ СООБЩЕНИЙ
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    text = message.text.strip()
    
    # Если это команда "назад" - игнорируем
    if text == "⬅️ Назад":
        return
    
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
        else:
            car1, car2 = text.split(" против ", 1)
        
        car1 = car1.strip()
        car2 = car2.strip()
        
        print(f"🔍 Сравниваем: '{car1}' и '{car2}'")
        
        info1 = car_db.find_car(car1)
        info2 = car_db.find_car(car2)
        
        response = "🔄 <b>Сравнение автомобилей:</b>\n\n"
        
        if info1:
            response += f"🚗 <b>{car1}</b>:\n"
            response += f"💰 Цена: {info1['price']}\n"
            response += f"⚙️ Двигатель: {info1['engine']}\n"
            response += f"⛽ Расход: {info1['fuel']}\n\n"
        else:
            response += f"❌ {car1} не найден\n\n"
        
        if info2:
            response += f"🚙 <b>{car2}</b>:\n"
            response += f"💰 Цена: {info2['price']}\n"
            response += f"⚙️ Двигатель: {info2['engine']}\n"
            response += f"⛽ Расход: {info2['fuel']}\n\n"
        else:
            response += f"❌ {car2} не найден\n\n"
        
        # Сравниваем цены если оба авто найдены
        if info1 and info2:
            price1 = car_db.get_price_number(info1['price'])
            price2 = car_db.get_price_number(info2['price'])
            
            if price1 > price2:
                response += f"💰 <b>Выгоднее: {car2}</b>"
            elif price2 > price1:
                response += f"💰 <b>Выгоднее: {car1}</b>"
            else:
                response += "💰 <b>Цены одинаковые</b>"
        
        bot.send_message(message.chat.id, response, parse_mode='HTML')
        
    except Exception as e:
        print(f"Ошибка сравнения: {e}")
        bot.send_message(
            message.chat.id,
            "❌ Ошибка. Используйте: 'Onix vs Tracker'",
            reply_markup=main_menu()
        )

def handle_single_car(message, text):
    """Обработка поиска одного автомобиля"""
    car_info = car_db.find_car(text)
    if car_info:
        response = f"🚗 <b>{text}</b>\n\n"
        response += f"💰 Цена: {car_info['price']}\n"
        response += f"⚙️ Двигатель: {car_info['engine']}\n"
        response += f"⛽ Расход: {car_info['fuel']}\n"
        response += f"📊 КПП: {car_info['transmission']}\n"
        response += f"🎯 Тип: {car_info['type']}\n"
        
        if 'features' in car_info:
            response += f"🔧 Опции: {', '.join(car_info['features'][:3])}"
        
        bot.send_message(message.chat.id, response, parse_mode='HTML')
    else:
        bot.send_message(
            message.chat.id,
            f"❌ '{text}' не найден.\nПопробуйте другое название или сравнение.",
            reply_markup=main_menu()
        )

print("✅ Бот запущен! Ошибок нет!")
bot.infinity_polling()
