# parsers/avtoelon_parser.py
import requests
from bs4 import BeautifulSoup
import time
import re

print("🎯 Улучшенный парсер Avtoelon загружен!")

class AvtoelonParser:
    def __init__(self):
        self.session = requests.Session()
        # Устанавливаем заголовки как у браузера
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        print("✅ Парсер готов к работе!")
    
    def get_car_info(self, car_name):
        """Получаем информацию об автомобиле"""
        try:
            print(f"🔍 Ищем информацию по: {car_name}")
            
            # Создаем URL для поиска
            url = f"https://avtoelon.uz/uz/avto/avtomobili-{car_name.lower()}/"
            print(f"🌐 Открываем: {url}")
            
            # Загружаем страницу
            response = self.session.get(url, timeout=15)
            print(f"📡 Статус ответа: {response.status_code}")
            
            if response.status_code != 200:
                return {"error": f"Сайт недоступен: {response.status_code}"}
            
            # Парсим HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем заголовок страницы
            title = soup.title.string if soup.title else "Не найден"
            print(f"📄 Заголовок страницы: {title}")
            
            # Ищем цены на странице
            prices = []
            price_elements = soup.find_all(text=re.compile(r'\$|сум', re.IGNORECASE))
            
            for price_text in price_elements[:10]:  # Берем первые 10
                clean_price = price_text.strip()
                if len(clean_price) < 50:  # Фильтруем длинные тексты
                    prices.append(clean_price)
                    print(f"💰 Найдена цена: {clean_price}")
            
            return {
                "car_name": car_name,
                "page_title": title,
                "prices_found": len(prices),
                "prices": prices[:5],  # Возвращаем первые 5 цен
                "status": "success"
            }
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return {"error": str(e), "status": "error"}

# Тестируем парсер
if __name__ == "__main__":
    print("🚀 Запускаем тестирование парсера...")
    
    parser = AvtoelonParser()
    
    # Тестируем на популярных машинах
    test_cars = ["cobalt", "nexia", "spark"]
    
    for car in test_cars:
        print(f"\n{'='*40}")
        print(f"🚗 ТЕСТИРУЕМ: {car.upper()}")
        result = parser.get_car_info(car)
        print(f"📊 РЕЗУЛЬТАТ: {result}")
        time.sleep(2)  # Ждем 2 секунды между запросами
    
    print("\n🎉 ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ!")
