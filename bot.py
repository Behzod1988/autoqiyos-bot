import os
import time
from threading import Thread
from flask import Flask
import telebot
from telebot import types

# Flask для удержания онлайн
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 AutoQiyos Bot работает 24/7!"

def run_flask():
    app.run(host='0.0.0.0', port=8080, debug=False)

# Запускаем Flask в отдельном потоке
Thread(target=run_flask, daemon=True).start()

# Бот
TOKEN = os.environ['BOT_TOKEN']
bot = telebot.TeleBot(TOKEN)

# Меню
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚗 Сравнить авто", "🔎 Поиск по сайту")
    markup.add("ℹ️ О проекте", "💬 Связаться")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🚘 <b>AutoQiyos Bot</b> работает 24/7!\nВыберите действие:",
        parse_mode='HTML',
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if message.text == "🚗 Сравнить авто":
        bot.send_message(message.chat.id, "Введите: Onix vs Tracker")
    elif message.text == "🔎 Поиск по сайту":
        bot.send_message(message.chat.id, "Введите марку авто для поиска")
    elif message.text == "ℹ️ О проекте":
        bot.send_message(message.chat.id, "🤖 AutoQiyos - бот для сравнения автомобилей\n\nРаботает 24/7 на Railway!")
    elif message.text == "💬 Связаться":
        bot.send_message(message.chat.id, "📞 Админ: @behzod_islomoff")
    else:
        bot.send_message(message.chat.id, "Используйте кнопки меню 👇", reply_markup=main_menu())

print("🤖 Бот запускается...")
while True:
    try:
        bot.polling(none_stop=True, timeout=60)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        time.sleep(5)
