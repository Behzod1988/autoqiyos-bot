import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class SimpleParser:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        print("✅ Настоящий парсер готов")
    
    def get_prices(self, car_name):
        """Парсинг реальных цен с Avtoelon.uz"""
        try:
            print(f"🔍 Ищем реальные объявления для: {car_name}")
            
            # Парсим Avtoelon
            avtoelon_results = self.parse_avtoelon(car_name)
            
            if avtoelon_results:
                return {
                    "car": car_name,
                    "prices": avtoelon_results,
                    "status": "success",
                    "total_found": len(avtoelon_results)
                }
            else:
                return {"error": "Не найдено объявлений", "status": "error"}
                
        except Exception as e:
            logger.error(f"Ошибка парсинга: {e}")
            return {"error": str(e), "status": "error"}
    
    def parse_avtoelon(self, car_name):
        """Парсинг Avtoelon.uz"""
        try:
            url = f"https://avtoelon.uz/uz/avto/?search={car_name}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            cars_data = []
            
            # Ищем карточки объявлений
            listings = soup.find_all('div', class_='list-item')[:8]
            
            for item in listings:
                try:
                    car_info = {}
                    
                    # Название
                    title_elem = item.find('span', class_='name')
                    if title_elem:
                        car_info['title'] = title_elem.text.strip()
                    
                    # Цена
                    price_elem = item.find('span', class_='price')
                    if price_elem:
                        car_info['price'] = price_elem.text.strip()
                    
                    # Год
                    year_elem = item.find('span', class_='year')
                    if year_elem:
                        car_info['year'] = year_elem.text.strip()
                    
                    car_info['source'] = 'Avtoelon.uz'
                    
                    if car_info.get('title') and car_info.get('price'):
                        cars_data.append(car_info)
                        
                except Exception:
                    continue
            
            print(f"✅ Найдено {len(cars_data)} объявлений")
            return cars_data
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return []
