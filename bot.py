import os
import time
import requests
from threading import Thread
from flask import Flask
import telebot
from telebot import types

print("🚀 AutoQiyos Bot запускается...")

# Проверяем токен
TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    print("❌ ОШИБКА: BOT_TOKEN не найден!")
    exit(1)

# 🔥 УСИЛЕННОЕ УДАЛЕНИЕ WEBHOOK
print("🗑️ Удаляем ВСЕ старые webhooks...")
try:
    # Способ 1: Через библиотеку
    bot = telebot.TeleBot(TOKEN)
    bot.delete_webhook()
    print("✅ Webhook удален через библиотеку")
    
    # Способ 2: Через прямой API запрос
    response = requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
    print(f"✅ Webhook удален через API: {response.status_code}")
    
    # Способ 3: С параметром drop_pending_updates
    response = requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true")
    print(f"✅ Webhook удален с очисткой: {response.status_code}")
    
    time.sleep(3)  # Даем время Telegram обработать
except Exception as e:
    print(f"⚠️ Ошибка при удалении webhook: {e}")

# Flask для удержания онлайн
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 AutoQiyos Bot работает 24/7!"

def run_flask():
    app.run(host='0.0.0.0', port=8080, debug=False)

Thread(target=run_flask, daemon=True).start()

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
        parse_mode='HTML', 
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    text = message.text
    
    if text == "🚗 Сравнить авто":
        bot.send_message(
            message.chat.id,
            "🔧 Введите два автомобиля для сравнения (например: <b>Onix vs Tracker</b>)",
            parse_mode='HTML', 
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
            parse_mode='HTML',
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

print("✅ Бот настроен. Запускаем polling...")
while True:
    try:
        bot.polling(none_stop=True, timeout=60)
        print("🔄 Перезапускаем polling...")
    except Exception as e:
        print(f"❌ Ошибка polling: {e}")
        time.sleep(5)
