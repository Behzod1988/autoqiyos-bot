# parsers/simple_parser.py
import requests
from bs4 import BeautifulSoup

print("✅ Простой парсер загружен!")

class SimpleParser:
    def __init__(self):
        print("🎯 Парсер готов!")
    
    def get_prices(self, car_name):
        """Простой парсинг цен"""
        try:
            url = f"https://avtoelon.uz/uz/avto/avtomobili-{car_name.lower()}/"
            print(f"🔍 Парсим: {car_name}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                # Просто ищем любые цены на странице
                soup = BeautifulSoup(response.text, 'html.parser')
                prices = []
                
                # Ищем тексты с $ или сум
                for text in soup.stripped_strings:
                    if '$' in text or 'сум' in text:
                        clean = text.strip()
                        if len(clean) < 50:  # Короткие тексты (скорее всего цены)
                            prices.append(clean)
                
                return {
                    "car": car_name,
                    "prices": prices[:5],  # Первые 5 цен
                    "url": url,
                    "status": "success"
                }
            else:
                return {"error": f"Ошибка {response.status_code}", "status": "error"}
                
        except Exception as e:
            return {"error": str(e), "status": "error"}
