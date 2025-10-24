import requests
from bs4 import BeautifulSoup
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SimpleParser:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        print("✅ Улучшенный парсер готов")
    
    def get_prices(self, car_name):
        """Парсинг реальных цен с Avtoelon.uz и OLX.uz"""
        try:
            print(f"🔍 Запускаем парсинг для: {car_name}")
            
            # Парсим оба сайта
            avtoelon_results = self.parse_avtoelon(car_name)
            olx_results = self.parse_olx(car_name)
            
            # Объединяем результаты
            all_ads = avtoelon_results + olx_results
            
            if all_ads:
                return {
                    "car": car_name,
                    "prices": all_ads,
                    "status": "success",
                    "total_found": len(all_ads),
                    "sources": f"Avtoelon.uz: {len(avtoelon_results)}, OLX.uz: {len(olx_results)}"
                }
            else:
                return {"error": "Не найдено объявлений", "status": "error"}
                
        except Exception as e:
            logger.error(f"Ошибка парсинга: {e}")
            return {"error": str(e), "status": "error"}
    
    def parse_avtoelon(self, car_name):
        """Парсинг Avtoelon.uz"""
        try:
            url = f"https://avtoelon.uz/uz/avto/?search={car_name}&sort=date"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            cars_data = []
            
            # Ищем карточки объявлений
            listings = soup.find_all('div', class_='list-item')[:10]
            
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
                    
                    # Ссылка
                    link_elem = item.find('a', href=True)
                    if link_elem:
                        car_info['link'] = f"https://avtoelon.uz{link_elem['href']}"
                    
                    car_info['source'] = 'Avtoelon.uz'
                    
                    if car_info.get('title') and car_info.get('price'):
                        cars_data.append(car_info)
                        
                except Exception as e:
                    continue
            
            print(f"✅ Avtoelon: найдено {len(cars_data)} объявлений")
            return cars_data
            
        except Exception as e:
            print(f"❌ Ошибка Avtoelon: {e}")
            return []
    
    def parse_olx(self, car_name):
        """Парсинг OLX.uz"""
        try:
            url = f"https://www.olx.uz/transport/avtomobili/q-{car_name}/"
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            cars_data = []
            
            # Ищем карточки объявлений OLX
            listings = soup.find_all('div', {'data-cy': 'l-card'})[:10]
            
            for item in listings:
                try:
                    car_info = {}
                    
                    # Заголовок
                    title_elem = item.find('h6', class_='css-16v5mdi')
                    if title_elem:
                        car_info['title'] = title_elem.text.strip()
                    
                    # Цена
                    price_elem = item.find('p', class_='css-10b0gli')
                    if price_elem:
                        car_info['price'] = price_elem.text.strip()
                    
                    # Местоположение
                    location_elem = item.find('p', class_='css-veheph')
                    if location_elem:
                        car_info['location'] = location_elem.text.strip()
                    
                    # Ссылка
                    link_elem = item.find('a', href=True)
                    if link_elem:
                        car_info['link'] = link_elem['href']
                    
                    car_info['source'] = 'OLX.uz'
                    
                    if car_info.get('title') and car_info.get('price'):
                        cars_data.append(car_info)
                        
                except Exception as e:
                    continue
            
            print(f"✅ OLX: найдено {len(cars_data)} объявлений")
            return cars_data
            
        except Exception as e:
            print(f"❌ Ошибка OLX: {e}")
            return []
