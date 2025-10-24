import os
import requests
import telebot
from telebot import types
import time

print("🚀 AutoQiyos Bot - УПРОЩЕННАЯ ВЕРСИЯ")

# Проверяем токен
TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    print("❌ ОШИБКА: Нет токена!")
    exit(1)

print("✅ Токен найден")

# Создаем бота с отключенным многопоточным поллингом
bot = telebot.TeleBot(TOKEN, parse_mode='HTML', threaded=False)

# Ждем 10 секунд чтобы старый бот точно остановился
print("⏳ Ждем остановки старого бота...")
time.sleep(10)

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

# ПРОСТЫЕ КНОПКИ
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚗 Сравнить авто")
    markup.add("🔍 Найти авто")
    markup.add("ℹ️ О проекте")
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
    bot.send_message(message.chat.id, "✅ Бот работает! Тест пройден.")

@bot.message_handler(commands=['debug'])
def debug(message):
    bot.send_message(message.chat.id, f"🔧 Статус: Работает\n🚗 Авто в базе: {len(car_db.data['cars'])}")

@bot.message_handler(func=lambda message: message.text == "🚗 Сравнить авто")
def compare_cars(message):
    bot.send_message(
        message.chat.id,
        "🔧 Напиши два автомобиля:\n\n<code>Onix vs Tracker</code>\n<code>Cobalt против Nexia</code>",
        parse_mode='HTML'
    )

@bot.message_handler(func=lambda message: message.text == "🔍 Найти авто")
def find_car(message):
    bot.send_message(
        message.chat.id,
        "🔍 Напиши название автомобиля:\n\n<code>Cobalt</code>\n<code>Nexia</code>\n<code>Onix</code>",
        parse_mode='HTML'
    )

@bot.message_handler(func=lambda message: message.text == "ℹ️ О проекте")
def about(message):
    bot.send_message(
        message.chat.id,
        "ℹ️ <b>AutoQiyos</b>\n\nПростой бот для сравнения автомобилей\n\nКоманды:\n/start - меню\n/test - проверка\n/debug - статус",
        parse_mode='HTML'
    )

# ОБРАБОТКА ВСЕХ СООБЩЕНИЙ
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    text = message.text.strip()
    
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
    
    # Поиск одного автомобиля
    else:
        info = car_db.find_car(text)
        if info:
            response = f"🚗 <b>{text}</b>\n\n"
            response += f"💰 {info['price']}\n"
            response += f"⚙️ {info['engine']}\n"
            response += f"⛽ {info['fuel']}\n"
            response += f"📊 {info['transmission']}"
            
            bot.send_message(message.chat.id, response, parse_mode='HTML')
        else:
            bot.send_message(
                message.chat.id,
                f"❌ '{text}' не найден\n\nПопробуй другое название.",
                reply_markup=main_menu()
            )

print("🎯 Запускаем упрощенного бота...")
try:
    # Используем простой polling без многопоточности
    bot.polling(none_stop=True, interval=2, timeout=30)
except Exception as e:
    print(f"❌ Ошибка: {e}")
    print("🔄 Перезапуск через 10 секунд...")
    time.sleep(10)
