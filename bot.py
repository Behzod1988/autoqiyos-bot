import os
import time
import logging
from threading import Thread
from flask import Flask
import telebot
from telebot import types

# Настраиваем логирование чтобы убрать лишние ошибки
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("🚀 AutoQiyos Bot запущен!")

TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    print("❌ BOT_TOKEN не найден!")
    exit(1)

# Создаем бота с настройками
bot = telebot.TeleBot(TOKEN, parse_mode='HTML')

# Тихий режим - убираем лишние логи telebot
telebot.logger.setLevel(logging.WARNING)

# Удаляем webhook без ошибок
try:
    bot.delete_webhook(drop_pending_updates=True)
    time.sleep(2)
    print("✅ Webhook очищен")
except Exception as e:
    print(f"ℹ️ Webhook: {e}")

# Flask app без предупреждений
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 AutoQiyos Bot работает 24/7!"

@app.route('/health')
def health():
    return "✅ OK"

def run_flask():
    # Запускаем Flask без debug режима
    from waitress import serve
    serve(app, host='0.0.0.0', port=8080)

# Запускаем Flask в фоне
Thread(target=run_flask, daemon=True).start()
print("🌐 Flask запущен")

# 🎯 КЛАВИАТУРЫ
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🚗 Сравнить авто"))
    markup.add(types.KeyboardButton("🔎 Поиск по сайту"))
    markup.add(types.KeyboardButton("ℹ️ О проекте"))
    markup.add(types.KeyboardButton("💬 Связаться с админом"))
    return markup

def back_button():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("⬅️ Назад в меню"))
    return markup

# 🎯 ОБРАБОТЧИКИ
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🚘 <b>AutoQiyos — сравни авто легко!</b>\n\nВыбери действие ниже 👇",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    text = message.text
    
    if text == "🚗 Сравнить авто":
        bot.send_message(
            message.chat.id,
            "🔧 Введите два автомобиля для сравнения (например: <b>Onix vs Tracker</b>)",
            reply_markup=back_button()
        )
    
    elif text == "🔎 Поиск по сайту":
        bot.send_message(
            message.chat.id,
            "🕵️ Введите марку или модель, чтобы найти объявления.",
            reply_markup=back_button()
        )
    
    elif text == "ℹ️ О проекте":
        bot.send_message(
            message.chat.id,
            "ℹ️ <b>AutoQiyos</b> — бот для сравнения авто из сайтов Узбекистана.",
            reply_markup=back_button()
        )
    
    elif text == "💬 Связаться с админом":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            "📩 Написать админу", 
            url="https://t.me/behzod_islomoff"
        ))
        bot.send_message(
            message.chat.id, 
            "📞 Связаться с админом:", 
            reply_markup=markup
        )
    
    elif text == "⬅️ Назад в меню":
        bot.send_message(
            message.chat.id, 
            "🏠 Главное меню:", 
            reply_markup=main_menu()
        )
    
    else:
        bot.send_message(
            message.chat.id,
            "❓ Команда не найдена. Выбери из меню ниже 👇", 
            reply_markup=main_menu()
        )

print("✅ Бот настроен. Ожидаем сообщения...")

# Запускаем бота с обработкой ошибок
def run_bot():
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"🔁 Перезапуск из-за: {e}")
            time.sleep(5)

run_bot()
