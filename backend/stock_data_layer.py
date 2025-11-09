"""
Stock Data Layer v2 - прямой запрос к Yahoo Finance API (без yfinance)
"""
import requests
from typing import Dict, List, Optional
import time

class StockDataProvider:
    def __init__(self):
        self.cache = {}
        self.cache_duration = 60  # секунды
        self.base_url = "https://query1.finance.yahoo.com"
        
        # Настройка сессии с полными заголовками браузера
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://finance.yahoo.com/'
        })
        
    def _is_cache_valid(self, key: str) -> bool:
        """Проверка валидности кэша"""
        if key not in self.cache:
            return False
        timestamp = self.cache[key].get('timestamp', 0)
        return time.time() - timestamp < self.cache_duration
    
    def get_stock_price(self, symbol: str) -> Optional[Dict]:
        """Получить цену акции/индекса через прямой API Yahoo Finance"""
        cache_key = f"stock_{symbol}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            # Используем v8 chart API (работает без ограничений)
            url = f"{self.base_url}/v8/finance/chart/{symbol}"
            params = {
                'interval': '1d',
                'range': '5d'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'chart' not in data or 'result' not in data['chart']:
                print(f"No data for {symbol}")
                return None
            
            results = data['chart']['result']
            if not results:
                print(f"No data for {symbol}")
                return None
            
            result = results[0]
            meta = result.get('meta', {})
            
            # Извлекаем данные
            current_price = meta.get('regularMarketPrice', 0)
            previous_close = meta.get('chartPreviousClose', 0)
            
            # Расчет изменения за 24ч
            if previous_close > 0:
                change_24h = ((current_price - previous_close) / previous_close) * 100
            else:
                change_24h = 0.0
            
            # Определяем тип актива и название
            instrument_type = meta.get('instrumentType', '').upper()
            if instrument_type == 'ETF' or 'ETF' in meta.get('longName', '').upper():
                asset_type = 'ETF'
            elif symbol.startswith('^'):
                asset_type = 'Index'
            elif instrument_type == 'EQUITY':
                asset_type = 'Stock'
            else:
                asset_type = 'Asset'
            
            # Получаем название
            name = meta.get('longName', meta.get('shortName', symbol))
            
            result = {
                'symbol': symbol,
                'name': name,
                'price': round(current_price, 2),
                'change_24h': round(change_24h, 2),
                'currency': meta.get('currency', 'USD'),
                'market_cap': 0,  # v8 API не возвращает market cap
                'volume': int(meta.get('regularMarketVolume', 0)),
                'type': asset_type
            }
            
            self.cache[cache_key] = {
                'data': result,
                'timestamp': time.time()
            }
            return result
            
        except Exception as e:
            print(f"Error fetching stock data for {symbol}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_multiple_stocks(self, symbols: List[str]) -> Dict[str, Dict]:
        """Получить данные по нескольким акциям/индексам"""
        results = {}
        
        # v8 API не поддерживает множественные символы, запрашиваем по одному
        for symbol in symbols:
            data = self.get_stock_price(symbol)
            if data:
                results[symbol] = data
        
        return results
    
    def search_stock(self, query: str) -> Optional[Dict]:
        """Поиск акции/индекса по названию или символу"""
        # Простая реализация - пробуем получить данные
        data = self.get_stock_price(query.upper())
        if data:
            return {
                'symbol': data['symbol'],
                'name': data['name'],
                'type': data['type']
            }
        return None
    
    def get_market_indices(self) -> Dict[str, Dict]:
        """Получить данные основных рыночных индексов"""
        indices = ['^GSPC', '^DJI', '^IXIC', '^RUT']
        return self.get_multiple_stocks(indices)
    
    def get_popular_stocks(self) -> Dict[str, Dict]:
        """Получить данные популярных акций"""
        stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'SPY', 'QQQ', 'VOO']
        return self.get_multiple_stocks(stocks)
