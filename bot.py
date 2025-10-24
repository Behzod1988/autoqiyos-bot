import os
import requests
from flask import Flask
import telebot
from telebot import types

print("🚀 AutoQiyos Bot запускается...")

# Импортируем парсер
from parsers.simple_parser import SimpleParser

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN, parse_mode='HTML')
bot.skip_pending = True

# Создаем парсер
parser = SimpleParser()

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
            print(f"✅ База: {len(self.data['cars'])} авто")
        except Exception as e:
            print(f"❌ Ошибка базы: {e}")
            self.data = {"cars": {}}
    
    def find_car(self, car_name):
        if not self.data:
            self.load_database()
        
        for car_key in self.data["cars"]:
            if car_name.lower() in car_key.lower():
                return self.data["cars"][car_key]
        return None

car_db = CarDatabase()

# Flask app
app = Flask(__name__)
@app.route('/')
def home():
    return "🤖 AutoQiyos Bot работает!"

# ПРОСТЫЕ КНОПКИ
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚗 Сравнить авто", "🌐 Парсить цены")
    markup.add("ℹ️ О проекте")
    return markup

# КОМАНДЫ
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🚘 <b>AutoQiyos с парсингом!</b>\n\nНажми кнопку ниже:",
        reply_markup=main_menu()
    )

@bot.message_handler(commands=['parse'])
def parse_car(message):
    """Простой парсинг"""
    try:
        parts = message.text.split(' ', 1)
        if len(parts) < 2:
            bot.send_message(message.chat.id, "Напиши: /parse cobalt")
            return
        
        car_name = parts[1].strip()
        msg = bot.send_message(message.chat.id, f"🔍 Ищу {car_name}...")
        
        result = parser.get_prices(car_name)
        
        if result.get('status') == 'success':
            response = f"🚗 <b>{car_name.upper()}</b>\n\n"
            
            if result['prices']:
                response += "💰 <b>Найденные цены:</b>\n"
                for price in result['prices']:
                    response += f"• {price}\n"
            else:
                response += "❌ Цены не найдены\n"
            
            response += f"\n🔗 <a href='{result['url']}'>Смотреть на Avtoelon</a>"
        else:
            response = f"❌ Ошибка: {result.get('error', 'Неизвестно')}"
        
        bot.edit_message_text(response, message.chat.id, msg.message_id, parse_mode='HTML')
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

@bot.message_handler(func=lambda message: message.text == "🌐 Парсить цены")
def parse_menu(message):
    bot.send_message(
        message.chat.id,
        "🔍 Напиши название авто:\n\nПример: Cobalt, Nexia, Spark",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda message: message.text == "🚗 Сравнить авто")
def compare_menu(message):
    bot.send_message(
        message.chat.id,
        "🔧 Напиши два авто:\n\nФормат: Onix vs Tracker",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda message: message.text == "ℹ️ О проекте")
def about(message):
    bot.send_message(
        message.chat.id,
        "ℹ️ <b>AutoQiyos</b>\nПарсим цены с Avtoelon.uz\n\nКоманда: /parse авто",
        parse_mode='HTML',
        reply_markup=main_menu()
    )

# ОБРАБОТКА СООБЩЕНИЙ
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.strip()
    
    # Если это сравнение
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
            
            response = "🔄 <b>Сравнение:</b>\n\n"
            
            if info1:
                response += f"🚗 <b>{car1}</b>:\n"
                response += f"💰 {info1['price']}\n"
                response += f"⚙️ {info1['engine']}\n\n"
            else:
                response += f"❌ {car1} не найден\n\n"
            
            if info2:
                response += f"🚙 <b>{car2}</b>:\n"
                response += f"💰 {info2['price']}\n"
                response += f"⚙️ {info2['engine']}\n\n"
            else:
                response += f"❌ {car2} не найден\n\n"
            
            bot.send_message(message.chat.id, response, parse_mode='HTML')
            
        except Exception as e:
            bot.send_message(message.chat.id, "❌ Ошибка. Используй: Onix vs Tracker")
    
    # Если это просто текст - парсим
    else:
        msg = bot.send_message(message.chat.id, f"🔍 Ищу '{text}'...")
        result = parser.get_prices(text)
        
        if result.get('status') == 'success':
            response = f"🚗 <b>{text.upper()}</b>\n\n"
            
            if result['prices']:
                response += "💰 <b>Цены:</b>\n"
                for price in result['prices']:
                    response += f"• {price}\n"
            else:
                response += "❌ Цены не найдены\n"
            
            response += f"\n🔗 <a href='{result['url']}'>Смотреть на Avtoelon</a>"
        else:
            response = f"❌ Не найден: {text}"
        
        bot.edit_message_text(response, message.chat.id, msg.message_id, parse_mode='HTML')

print("✅ Бот запущен!")
bot.infinity_polling()
