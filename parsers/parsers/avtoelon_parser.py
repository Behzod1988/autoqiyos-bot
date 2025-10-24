# parsers/avtoelon_parser.py
import requests
from bs4 import BeautifulSoup
import time

print("🎯 Простой парсер Avtoelon загружен!")

class SimpleAvtoelonParser:
    def __init__(self):
        print("✅ Парсер создан!")
    
    def test_connection(self):
        """Просто проверяем, что можем подключиться к сайту"""
        try:
            url = "https://avtoelon.uz"
            print(f"🔗 Пробуем подключиться к {url}")
            
            response = requests.get(url, timeout=10)
            print(f"📡 Статус: {response.status_code}")
            
            if response.status_code == 200:
                print("🎉 Ура! Сайт доступен!")
                return True
            else:
                print("😞 Сайт не доступен")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return False

# Тестируем при запуске
if __name__ == "__main__":
    print("🧪 Запускаем тест парсера...")
    parser = SimpleAvtoelonParser()
    parser.test_connection()
    print("🏁 Тест завершен!")
