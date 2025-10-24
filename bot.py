import os
import requests
import telebot
from telebot import types
from flask import Flask
from threading import Thread
import time

print("🚀 AutoQiyos Bot запускается...")

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN, parse_mode='HTML')

# ✅ ФИКСИМ ОШИБКУ 409
bot.skip_pending = True  # Пропускаем ожидающие сообщения

# Удаляем webhook и даем время для остановки старого бота
try:
    bot.delete_webhook(drop_pending_updates=True)
    print("✅ Webhook удален")
    time.sleep(3)  # Даем время остановиться старому боту
except Exception as e:
    print(f"⚠️ Ошибка webhook: {e}")

# БАЗА ДАННЫХ
class CarDatabase:
    def __init__(self):
        self.db_url = "https://raw.githubusercontent.com/Behzod1988/autoqiyos-bot/main/car_database.json"
        self.data = None
        self.load_database()
    
    def load_database(self):
        try:
            response = requests.get(self.db_url, timeout=10)
            self.data = response.json()
            print(f"✅ База загружена: {len(self.data['cars'])} авто")
        except Exception as e:
            print(f"❌ Ошибка базы: {e}")
            self.data = {"cars": {}}
    
    def find_car(self, car_name):
        if not self.data:
            self.load_database()
        
        car_name_lower = car_name.lower().strip()
        for car_key in self.data["cars"]:
            if car_name_lower in car_key.lower():
                return self.data["cars"][car_key]
        return None

car_db = CarDatabase()

# Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 AutoQiyos Bot работает!"

@app.route('/health')
def health():
    return {"status": "healthy", "cars": len(car_db.data["cars"])}

def run_flask():
    app.run(host='0.0.0.0', port=8080, debug=False)

Thread(target=run_flask, daemon=True).start()

# КЛАВИАТУРЫ
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚗 Сравнить авто", "🔍 Найти авто")
    markup.add("ℹ️ О проекте")
    return markup

def back_button():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("⬅️ Назад")
    return markup

# КОМАНДЫ
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🚘 <b>AutoQiyos - сравнение автомобилей</b>\n\nВыберите действие:",
        reply_markup=main_menu()
    )

@bot.message_handler(commands=['test'])
def test(message):
    bot.send_message(message.chat.id, "✅ Бот работает! Ошибок нет.")

@bot.message_handler(commands=['restart'])
def restart(message):
    bot.send_message(message.chat.id, "🔄 Перезапускаю бота...")
    # Перезапускаем бота
    bot.stop_polling()
    time.sleep(2)
    start_polling()

@bot.message_handler(func=lambda message: message.text == "🚗 Сравнить авто")
def compare_cars(message):
    bot.send_message(
        message.chat.id,
        "🔧 Введите два автомобиля для сравнения:\n\n<b>Формат:</b>\n<code>Onix vs Tracker</code>",
        parse_mode='HTML',
        reply_markup=back_button()
    )

@bot.message_handler(func=lambda message: message.text == "🔍 Найти авто")
def find_car(message):
    bot.send_message(
        message.chat.id,
        "🔍 Введите название автомобиля для поиска в базе:",
        reply_markup=back_button()
    )

@bot.message_handler(func=lambda message: message.text == "ℹ️ О проекте")
def about(message):
    bot.send_message(
        message.chat.id,
        "ℹ️ <b>AutoQiyos</b>\n\nБот для сравнения автомобилей\n\n"
        "🚗 Сравнивайте характеристики\n"
        "🔍 Ищите в базе данных\n"
        "💰 Актуальные цены",
        parse_mode='HTML',
        reply_markup=back_button()
    )

@bot.message_handler(func=lambda message: message.text == "⬅️ Назад")
def back(message):
    bot.send_message(message.chat.id, "Главное меню:", reply_markup=main_menu())

# ОБРАБОТКА СООБЩЕНИЙ
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    text = message.text.strip()
    
    if text == "⬅️ Назад":
        return
    
    # Обработка сравнения
    if " vs " in text.lower() or " против " in text.lower():
        try:
            if " vs " in text.lower():
                car1, car2 = text.split(" vs ", 1)
            else:
                car1, car2 = text.split(" против ", 1)
            
            car1 = car1.strip()
            car2 = car2.strip()
            
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
            
            bot.send_message(message.chat.id, response, parse_mode='HTML')
            
        except Exception as e:
            print(f"Ошибка сравнения: {e}")
            bot.send_message(message.chat.id, "❌ Ошибка. Используйте: Onix vs Tracker")
    
    # Поиск одного автомобиля
    else:
        info = car_db.find_car(text)
        if info:
            response = f"🚗 <b>{text}</b>\n\n"
            response += f"💰 Цена: {info['price']}\n"
            response += f"⚙️ Двигатель: {info['engine']}\n"
            response += f"⛽ Расход: {info['fuel']}\n"
            response += f"📊 КПП: {info['transmission']}\n"
            response += f"🎯 Тип: {info['type']}"
            
            bot.send_message(message.chat.id, response, parse_mode='HTML')
        else:
            bot.send_message(
                message.chat.id,
                f"❌ '{text}' не найден в базе данных\n\nПопробуйте другое название.",
                reply_markup=main_menu()
            )

# ФУНКЦИЯ ЗАПУСКА ПОЛЛИНГА
def start_polling():
    print("🔄 Запускаем поллинг...")
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=30)
    except Exception as e:
        print(f"❌ Ошибка поллинга: {e}")
        print("🔄 Перезапускаем через 5 секунд...")
        time.sleep(5)
        start_polling()

print("✅ Бот готов к работе!")
start_polling()
