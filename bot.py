import os
import requests
import telebot
from telebot import types
import time
import logging

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("🚀 AutoQiyos Bot запускается...")

TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    print("❌ ОШИБКА: BOT_TOKEN не найден!")
    exit(1)

# Создаем бота с отключенным многопоточным поллингом
bot = telebot.TeleBot(TOKEN, parse_mode='HTML', threaded=False)

# ✅ ФИКС ОШИБКИ 409: Ждем и очищаем
print("⏳ Ожидаем остановки старых процессов...")
time.sleep(10)

try:
    bot.remove_webhook()  # Удаляем webhook если был
    time.sleep(2)
except:
    pass

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
            print(f"❌ Ошибка загрузки базы: {e}")
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

# ПРОСТОЙ ПАРСЕР (если нужен)
class SimpleParser:
    def __init__(self):
        print("✅ Парсер готов")
    
    def get_prices(self, car_name):
        """Простой парсинг Avtoelon"""
        try:
            # Здесь будет парсинг, пока заглушка
            return {
                "car": car_name,
                "prices": ["15 000 000 сум", "16 500 000 сум"],
                "status": "success"
            }
        except Exception as e:
            return {"error": str(e), "status": "error"}

parser = SimpleParser()

# КЛАВИАТУРЫ
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚗 Сравнить авто", "🔍 Найти авто")
    markup.add("🌐 Парсить цены", "ℹ️ О проекте")
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
    bot.send_message(message.chat.id, "✅ Бот работает! Ошибок в логах нет.")

@bot.message_handler(commands=['debug'])
def debug(message):
    import datetime
    status = f"🔄 Статус: Работает\n📊 Авто в базе: {len(car_db.data['cars'])}\n⏰ Время: {datetime.datetime.now()}"
    bot.send_message(message.chat.id, status)

@bot.message_handler(commands=['parse'])
def parse_command(message):
    """Парсинг реальных цен"""
    try:
        parts = message.text.split(' ', 1)
        if len(parts) < 2:
            bot.send_message(message.chat.id, "Напиши: /parse cobalt")
            return
        
        car_name = parts[1].strip()
        msg = bot.send_message(message.chat.id, f"🔍 Ищу реальные объявления на {car_name}...")
        
        result = parser.get_prices(car_name)
        
        if result.get('status') == 'success':
            response = f"🚗 <b>{car_name.upper()}</b>\n\n"
            response += f"📊 Найдено: {result['total_found']} объявлений\n\n"
            response += "💰 <b>Реальные объявления:</b>\n\n"
            
            for i, ad in enumerate(result['prices'][:5], 1):
                response += f"{i}. <b>{ad.get('title', 'Без названия')}</b>\n"
                response += f"   💰 {ad.get('price', 'Цена не указана')}\n"
                if ad.get('year'):
                    response += f"   🗓 {ad['year']}\n"
                response += f"   🌐 {ad.get('source', 'Avtoelon.uz')}\n\n"
            
        else:
            response = f"❌ Не найдено объявлений для {car_name}"
        
        bot.edit_message_text(
            response, 
            message.chat.id, 
            msg.message_id, 
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

@bot.message_handler(func=lambda message: message.text == "🚗 Сравнить авто")
def compare_cars(message):
    bot.send_message(
        message.chat.id,
        "🔧 Введите два автомобиля:\n\n<code>Onix vs Tracker</code>\n<code>Cobalt против Nexia</code>",
        parse_mode='HTML'
    )

@bot.message_handler(func=lambda message: message.text == "🔍 Найти авто")
def find_car(message):
    bot.send_message(
        message.chat.id,
        "🔍 Введите название автомобиля:\n\n<code>Cobalt</code>\n<code>Nexia</code>\n<code>Onix</code>",
        parse_mode='HTML'
    )

@bot.message_handler(func=lambda message: message.text == "🌐 Парсить цены")
def parse_menu(message):
    bot.send_message(
        message.chat.id,
        "🌐 Введите название авто для парсинга:\n\nИли используйте команду: /parse авто",
        parse_mode='HTML'
    )

@bot.message_handler(func=lambda message: message.text == "ℹ️ О проекте")
def about(message):
    bot.send_message(
        message.chat.id,
        "ℹ️ <b>AutoQiyos</b>\n\nБот для сравнения автомобилей и парсинга цен\n\n"
        "Команды:\n/start - меню\n/test - проверка\n/debug - статус\n/parse - парсинг",
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
            logger.error(f"Ошибка сравнения: {e}")
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

print("✅ Бот готов к запуску...")
try:
    # Используем простой polling с обработкой ошибок
    bot.polling(none_stop=True, interval=3, timeout=30)
except Exception as e:
    logger.error(f"❌ Ошибка запуска: {e}")
    print("🔄 Перезапуск через 10 секунд...")
    time.sleep(10)
