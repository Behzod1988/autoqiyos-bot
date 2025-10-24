import os
import telebot
from flask import Flask
from threading import Thread

print("🚀 Запускаем простого бота...")

# Проверяем токен
TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    print("❌ ОШИБКА: BOT_TOKEN не найден!")
    exit(1)

print("✅ Токен найден")

bot = telebot.TeleBot(TOKEN)

# Простой Flask для Railway
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Бот работает!"

def run_flask():
    app.run(host='0.0.0.0', port=8080, debug=False)

Thread(target=run_flask, daemon=True).start()

# Простая команда
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "✅ Бот работает! Привет!")

@bot.message_handler(commands=['test'])
def test(message):
    bot.send_message(message.chat.id, "✅ Тест пройден! Бот отвечает!")

@bot.message_handler(func=lambda message: True)
def echo(message):
    bot.send_message(message.chat.id, f"Вы написали: {message.text}")

print("✅ Бот запускается...")
try:
    bot.infinity_polling()
except Exception as e:
    print(f"❌ Ошибка: {e}")
