# 🤖 AutoQiyos Bot - Умный бот для сравнения автомобилей

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue.svg)
![Railway](https://img.shields.io/badge/Deployed-Railway-success.svg)

Telegram бот для интеллектуального сравнения характеристик и цен автомобилей с автоматической синхронизацией базы данных через GitHub.

## ✨ Возможности

- 🔄 **Сравнение автомобилей** - Детальное сравнение двух авто по цене и характеристикам
- 🔍 **Умный поиск** - Поиск автомобилей с системой релевантности
- 💰 **Анализ цен** - Определение выгодного варианта при сравнении
- 🚀 **Автообновление** - База обновляется каждый час
- 📊 **Полная база** - Просмотр всех доступных марок

## 🚀 Быстрый запуск

### 1. Запуск на Railway (рекомендуется)

1. Создайте бота через [@BotFather](https://t.me/BotFather)
2. Разверните на [Railway](https://railway.app)
3. Укажите переменную окружения:
   - `BOT_TOKEN` - токен вашего бота

### 2. Локальная установка

```bash
# Клонировать репозиторий
git clone https://github.com/Behzod1988/autoqiyos-bot.git
cd autoqiyos-bot

# Установить зависимости
pip install -r requirements.txt

# Запустить бота
python bot.py
```

## 🎯 Использование

### Основные команды:
- `/start` - Главное меню
- `/update` - Обновить базу данных

### Функции через меню:
- 🚗 **Сравнить авто** - Сравнить два автомобиля
- 🔎 **Найти авто** - Поиск информации об автомобиле
- 📊 **Все марки** - Полный список автомобилей
- 🔄 **Обновить базу** - Принудительное обновление

### Примеры:
```
Onix vs Tracker
Cobalt
Nexia 3
```

## 🔧 Разработка

### Добавление автомобилей:
Редактируйте файл `car_database.json`:

```json
{
  "Chevrolet Onix": {
    "price": "15 000$",
    "engine": "1.0L Turbo",
    "fuel": "5.8 л/100km",
    "transmission": "Автомат",
    "type": "Седан"
  }
}
```

## 📞 Контакты

- **Разработчик**: [Behzod Islomoff](https://t.me/behzod_islomoff)
- **GitHub**: [Behzod1988](https://github.com/Behzod1988)
- **Issues**: [Сообщить об ошибке](https://github.com/Behzod1988/autoqiyos-bot/issues)

---

<div align="center">

**⭐ Если проект полезен, поставьте звезду на GitHub!**

</div>
