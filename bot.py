import os
import time
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

# Создаем бота
bot = telebot.TeleBot(TOKEN)

# 🔥 УДАЛЯЕМ СТАРЫЙ WEBHOOK
try:
    bot.delete_webhook()
    print("✅ Старый webhook удален!")
    time.sleep(1)
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

# 🎯 КЛАВИАТУРЫ КАК ВЧЕРА
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

# 🎯 ОБРАБОТЧИКИ КАК ВЧЕРА
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
            "ℹ️ <b>AutoQiyos</b> — бот для сравнения авто из сайтов Узбекистана.\n\n"
            "⚡ <b>Возможности:</b>\n"
            "• Сравнение характеристик авто\n"
            "• Поиск объявлений\n"
            "• Анализ цен\n"
            "• Работает 24/7",
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
        # Обработка сравнения авто
        if " vs " in text.lower() or " против " in text.lower():
            try:
                if " vs " in text:
                    car1, car2 = text.split(" vs ", 1)
                else:
                    car1, car2 = text.split(" против ", 1)
                
                response = (
                    f"🔄 <b>Сравниваю автомобили:</b>\n\n"
                    f"🚗 <b>{car1.strip()}</b>\n"
                    f"⚔️ VS\n" 
                    f"🚙 <b>{car2.strip()}</b>\n\n"
                    f"📊 <i>Функция сравнения в разработке...</i>\n"
                    f"Скоро будут доступны:\n"
                    f"• Цены\n• Характеристики\n• Отзывы\n• Рейтинги"
                )
                bot.send_message(message.chat.id, response, parse_mode='HTML')
                
            except:
                bot.send_message(
                    message.chat.id,
                    "❌ Используйте формат: <b>Onix vs Tracker</b>",
                    parse_mode='HTML'
                )
        else:
            bot.send_message(
                message.chat.id,
                "❓ Команда не найдена. Выбери из меню ниже 👇", 
                reply_markup=main_menu()
            )

print("✅ Бот настроен. Запускаем...")
while True:
    try:
        bot.polling(none_stop=True, timeout=60)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        time.sleep(5)
