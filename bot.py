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

# Удаляем webhook
try:
    bot.delete_webhook(drop_pending_updates=True)
    time.sleep(1)
except:
    pass

# КЛАСС ДЛЯ РАБОТЫ С БАЗОЙ ДАННЫХ
class CarDatabase:
    def __init__(self):
        # ЗАМЕНИТЕ 'ВАШ_USERNAME' НА ВАШ РЕАЛЬНЫЙ USERNAME GITHUB!
        self.db_url = "https://raw.githubusercontent.com/ВАШ_USERNAME/autoqiyos-bot/main/car_database.json"
        self.data = None
    
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
        
        # Поиск по точному совпадению
        for car_key in self.data["cars"]:
            if car_name_lower == car_key.lower():
                return self.data["cars"][car_key]
        
        # Поиск по частичному совпадению
        for car_key in self.data["cars"]:
            if car_name_lower in car_key.lower() or car_key.lower() in car_name_lower:
                return self.data["cars"][car_key]
        
        return None

# Инициализируем базу
car_db = CarDatabase()

# Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 AutoQiyos Bot с базой данных работает!"

def run_flask():
    app.run(host='0.0.0.0', port=8080, debug=False)

Thread(target=run_flask, daemon=True).start()

# Клавиатуры
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚗 Сравнить авто", "🔎 Поиск по сайту")
    markup.add("ℹ️ О проекте", "💬 Связаться")
    return markup

def back_button():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("⬅️ Назад в меню")
    return markup

# Обработчики
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🚘 <b>AutoQiyos — сравни авто легко!</b>\n\nВыбери действие:",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda message: message.text == "🚗 Сравнить авто")
def start_comparison(message):
    bot.send_message(
        message.chat.id,
        "🔧 Введите два автомобиля для сравнения:\n\n<b>Формат:</b>\nOnix vs Tracker\nИли\nOnix против Tracker",
        parse_mode='HTML',
        reply_markup=back_button()
    )

@bot.message_handler(func=lambda message: message.text == "🔎 Поиск по сайту")
def start_search(message):
    bot.send_message(
        message.chat.id,
        "🕵️ Введите марку или модель, чтобы найти объявления.",
        reply_markup=back_button()
    )

@bot.message_handler(func=lambda message: message.text == "ℹ️ О проекте")
def about_project(message):
    bot.send_message(
        message.chat.id,
        "ℹ️ <b>AutoQiyos</b> — бот для сравнения авто с реальной базой данных!\n\nТеперь с реальными ценами и характеристиками!",
        parse_mode='HTML',
        reply_markup=back_button()
    )

@bot.message_handler(func=lambda message: message.text == "💬 Связаться")
def contact_admin(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📞 Написать админу", url="https://t.me/behzod_islomoff"))
    bot.send_message(message.chat.id, "Связь с админом:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "⬅️ Назад в меню")
def back_to_menu(message):
    bot.send_message(message.chat.id, "🏠 Главное меню:", reply_markup=main_menu())

# ОБРАБОТЧИК СРАВНЕНИЯ АВТО - ДОЛЖЕН БЫТЬ ПОСЛЕДНИМ
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    text = message.text
    
    # Проверяем на сравнение (должно быть после всех конкретных обработчиков)
    if " vs " in text.lower() or " против " in text.lower():
        try:
            # Определяем разделитель
            if " vs " in text:
                car1, car2 = text.split(" vs ", 1)
            else:
                car1, car2 = text.split(" против ", 1)
            
            car1 = car1.strip()
            car2 = car2.strip()
            
            print(f"🔍 Сравниваем: '{car1}' vs '{car2}'")
            
            info1 = car_db.find_car(car1)
            info2 = car_db.find_car(car2)
            
            if info1 and info2:
                response = f"🔄 <b>Сравнение автомобилей:</b>\n\n"
                
                response += f"🚗 <b>{car1}</b>:\n"
                response += f"💰 Цена: {info1['price']}$\n"
                response += f"⚙️ Двигатель: {info1['engine']}\n"
                response += f"⛽ Расход: {info1['fuel']} л/100km\n"
                response += f"📊 КПП: {info1['transmission']}\n"
                response += f"🎯 Тип: {info1['type']}\n\n"
                
                response += f"🚙 <b>{car2}</b>:\n" 
                response += f"💰 Цена: {info2['price']}$\n"
                response += f"⚙️ Двигатель: {info2['engine']}\n"
                response += f"⛽ Расход: {info2['fuel']} л/100km\n"
                response += f"📊 КПП: {info2['transmission']}\n"
                response += f"🎯 Тип: {info2['type']}\n\n"
                
                response += f"📅 <i>Данные актуальны на: {car_db.data.get('last_updated', 'N/A')}</i>"
                
            elif info1:
                response = f"❌ Автомобиль '{car2}' не найден в базе\n\n"
                response += f"🚗 <b>{car1}</b>:\n"
                response += f"💰 Цена: {info1['price']}$\n"
                response += f"⚙️ Двигатель: {info1['engine']}\n"
                response += f"⛽ Расход: {info1['fuel']} л/100km"
                
            elif info2:
                response = f"❌ Автомобиль '{car1}' не найден в базе\n\n"
                response += f"🚙 <b>{car2}</b>:\n"
                response += f"💰 Цена: {info2['price']}$\n"
                response += f"⚙️ Двигатель: {info2['engine']}\n"
                response += f"⛽ Расход: {info2['fuel']} л/100km"
                
            else:
                response = "❌ Оба автомобиля не найдены в базе данных"
                
            bot.send_message(message.chat.id, response, parse_mode='HTML')
            
        except Exception as e:
            print(f"Ошибка сравнения: {e}")
            bot.send_message(message.chat.id, "❌ Ошибка при сравнении. Используйте формат: 'Onix vs Tracker'")
    
    else:
        # Если не сравнение, ищем информацию об одном авто
        car_info = car_db.find_car(text)
        if car_info:
            response = f"🚗 <b>{text}</b>\n\n"
            response += f"💰 Цена: {car_info['price']}$\n"
            response += f"⚙️ Двигатель: {car_info['engine']}\n"
            response += f"⛽ Расход: {car_info['fuel']} л/100km\n"
            response += f"📊 КПП: {car_info['transmission']}\n"
            response += f"🎯 Тип: {car_info['type']}\n"
            response += f"📅 Годы: {car_info['years']}\n\n"
            response += f"🔧 Опции: {', '.join(car_info['features'])}"
            bot.send_message(message.chat.id, response, parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, "❓ Команда не найдена. Выберите действие 👇", reply_markup=main_menu())

print("✅ Бот с базой данных запущен!")
bot.infinity_polling()
