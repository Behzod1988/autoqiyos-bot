import os
import requests
from flask import Flask
from threading import Thread
import telebot
from telebot import types
from bs4 import BeautifulSoup

print("🚀 AutoQiyos Bot запускается...")

TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN, parse_mode='HTML')
bot.skip_pending = True

# Удаляем webhook
try:
    bot.delete_webhook(drop_pending_updates=True)
    print("✅ Webhook очищен")
except:
    print("⚠️ Ошибка webhook")

# ПРОСТОЙ ПАРСЕР ВНУТРИ ФАЙЛА
class SimpleParser:
    def __init__(self):
        print("✅ Парсер готов")
    
    def get_prices(self, car_name):
        """Простой парсинг Avtoelon"""
        try:
            url = f"https://avtoelon.uz/uz/avto/avtomobili-{car_name.lower()}/"
            print(f"🔍 Парсим: {url}")
            
            # Простой запрос
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Ищем цены
                prices = []
                for text in soup.stripped_strings:
                    if '$' in text or 'сум' in text:
                        clean = text.strip()
                        if len(clean) < 50:
                            prices.append(clean)
                
                return {
                    "car": car_name,
                    "prices": prices[:3],
                    "url": url,
                    "status": "success"
                }
            else:
                return {"error": f"Ошибка {response.status_code}", "status": "error"}
                
        except Exception as e:
            return {"error": str(e), "status": "error"}

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
    return {"status": "ok"}

def run_flask():
    app.run(host='0.0.0.0', port=8080, debug=False)

Thread(target=run_flask, daemon=True).start()

# ПРОСТЫЕ КНОПКИ
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚗 Сравнить авто", "🌐 Парсить Avtoelon")
    markup.add("📊 База данных", "ℹ️ О проекте")
    return markup

# КОМАНДЫ
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🚘 <b>AutoQiyos Bot</b>\n\n"
        "Выберите действие:",
        reply_markup=main_menu()
    )

@bot.message_handler(commands=['test'])
def test(message):
    """Простая тестовая команда"""
    bot.send_message(message.chat.id, "✅ Бот работает!")

@bot.message_handler(commands=['parse'])
def parse_command(message):
    """Парсинг через команду"""
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
                response += "💰 <b>Найдены цены:</b>\n"
                for price in result['prices']:
                    response += f"• {price}\n"
            else:
                response += "❌ Цены не найдены\n"
            
            response += f"\n🔗 <a href='{result['url']}'>Смотреть на Avtoelon</a>"
        else:
            response = f"❌ Ошибка: {result.get('error')}"
        
        bot.edit_message_text(response, message.chat.id, msg.message_id, parse_mode='HTML')
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

@bot.message_handler(func=lambda message: message.text == "🌐 Парсить Avtoelon")
def parse_menu(message):
    bot.send_message(
        message.chat.id,
        "🔍 Напиши название автомобиля:\n\nПример: Cobalt, Nexia, Spark",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda message: message.text == "🚗 Сравнить авто")
def compare_menu(message):
    bot.send_message(
        message.chat.id,
        "🔧 Напиши два автомобиля:\n\nФормат: Onix vs Tracker",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda message: message.text == "📊 База данных")
def database_menu(message):
    bot.send_message(
        message.chat.id,
        "📊 Напиши название авто из базы данных",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda message: message.text == "ℹ️ О проекте")
def about(message):
    bot.send_message(
        message.chat.id,
        "ℹ️ <b>AutoQiyos Bot</b>\n\n"
        "Простой бот для сравнения автомобилей\n\n"
        "Команды:\n"
        "/start - начать\n"
        "/test - проверить бота\n"
        "/parse авто - парсить цены",
        parse_mode='HTML',
        reply_markup=main_menu()
    )

# ОБРАБОТКА ВСЕХ СООБЩЕНИЙ
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    text = message.text.strip()
    
   
