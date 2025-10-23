import os
import time
import telebot
from flask import Flask
from threading import Thread

print("🚀 БОТ ЗАПУСКАЕТСЯ...")

# Проверяем токен
TOKEN = os.environ.get('BOT_TOKEN')
print(f"🔑 Токен: {'ЕСТЬ' if TOKEN else 'НЕТ'}")

if not TOKEN:
    print("❌ ОШИБКА: BOT_TOKEN не найден!")
    exit(1)

# Создаем бота
bot = telebot.TeleBot(TOKEN)

# 🔥 ВАЖНО: УДАЛЯЕМ WEBHOOK ПЕРЕД ЗАПУСКОМ
print("🗑️ Удаляем старый webhook...")
try:
    bot.delete_webhook()
    print("✅ Webhook удален!")
    time.sleep(1)
except Exception as e:
    print(f"⚠️ Ошибка при удалении webhook: {e}")

# Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ AutoQiyos Bot работает 24/7!"

@app.route('/health')
def health():
    return "🟢 HEALTHY"

def run_flask():
    print("🌐 Запускаем Flask на 0.0.0.0:8080...")
    app.run(host='0.0.0.0', port=8080, debug=False)

# Запускаем Flask в фоне
Thread(target=run_flask, daemon=True).start()

@bot.message_handler(commands=['start'])
def start(message):
    print(f"📩 Получен /start от {message.from_user.id}")
    bot.send_message(
        message.chat.id,
        "🚗 <b>AutoQiyos Bot</b> работает на Railway 24/7! ✅\n\n"
        "Доступные команды:\n"
        "• /start - меню\n" 
        "• /test - проверка\n"
        "• /status - статус бота\n\n"
        "Выберите действие:",
        parse_mode='HTML'
    )

@bot.message_handler(commands=['test', 'status'])
def test(message):
    bot.send_message(message.chat.id, "✅ Тест пройден! Бот активен и работает.")

@bot.message_handler(func=lambda message: True)
def all_messages(message):
    bot.send_message(message.chat.id, f"🤖 Вы написали: {message.text}")

print("🤖 Запускаем Telegram бота...")
while True:
    try:
        bot.polling(none_stop=True, timeout=30)
        print("🔄 Перезапускаем polling...")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        time.sleep(5)
