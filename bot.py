import os
import time
from threading import Thread
from flask import Flask
import telebot
from telebot import types

print("🎯 ТЕСТОВЫЙ ЗАПУСК БОТА...")

TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    print("❌ BOT_TOKEN не найден!")
    exit(1)

print(f"✅ Токен получен: {TOKEN[:10]}...")

# Создаем бота
bot = telebot.TeleBot(TOKEN)

# Удаляем webhook
try:
    bot.delete_webhook()
    print("✅ Webhook удален")
    time.sleep(2)
except Exception as e:
    print(f"⚠️ Ошибка удаления webhook: {e}")

# Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 AutoQiyos Bot ONLINE"

def run_flask():
    app.run(host='0.0.0.0', port=8080, debug=False)

Thread(target=run_flask, daemon=True).start()

# Главное меню
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🚗 Сравнить авто", "🔎 Поиск по сайту")
    markup.add("ℹ️ О проекте", "💬 Связаться")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    print(f"📩 Получен /start от {message.from_user.id}")
    bot.send_message(
        message.chat.id,
        "🚘 <b>AutoQiyos Bot</b>\n\n✅ Работает на Railway!\n\nВыберите действие:",
        parse_mode='HTML',
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    if message.text == "🚗 Сравнить авто":
        bot.send_message(message.chat.id, "Напишите: Onix vs Tracker")
    elif message.text == "🔎 Поиск по сайту":
        bot.send_message(message.chat.id, "Введите марку авто")
    elif message.text == "ℹ️ О проекте":
        bot.send_message(message.chat.id, "AutoQiyos - бот для сравнения авто")
    elif message.text == "💬 Связаться":
        bot.send_message(message.chat.id, "Админ: @behzod_islomoff")
    else:
        bot.send_message(message.chat.id, "Используйте кнопки меню 👇", reply_markup=main_menu())

print("🤖 Запускаем бота...")
bot.polling(none_stop=True, timeout=30)
