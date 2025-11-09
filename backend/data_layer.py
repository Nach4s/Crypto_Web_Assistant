"""
Data Layer - получение данных с CoinGecko и Binance API
"""
import requests
import aiohttp
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import time

class CryptoDataProvider:
    def __init__(self):
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        self.binance_base = "https://api.binance.com/api/v3"
        self.cache = {}
        self.cache_duration = 60  # секунды
        
    def _is_cache_valid(self, key: str) -> bool:
        """Проверка валидности кэша"""
        if key not in self.cache:
            return False
        timestamp = self.cache[key].get('timestamp', 0)
        return time.time() - timestamp < self.cache_duration
    
    def get_coin_price(self, coin_id: str = "bitcoin") -> Optional[Dict]:
        """Получить текущую цену монеты с CoinGecko (упрощенный метод)"""
        cache_key = f"price_{coin_id}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            url = f"{self.coingecko_base}/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_market_cap': 'true',
                'include_24hr_vol': 'true'
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Проверяем, что монета найдена
            if coin_id not in data:
                return None
            
            self.cache[cache_key] = {
                'data': data,
                'timestamp': time.time()
            }
            return data
        except Exception as e:
            print(f"Error fetching price for {coin_id}: {e}")
            return None
    
    def get_any_coin_data(self, coin_id: str) -> Optional[Dict]:
        """Получить данные любой монеты (универсальный метод)"""
        cache_key = f"any_coin_{coin_id}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            # Сначала пробуем упрощенный API
            url = f"{self.coingecko_base}/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_market_cap': 'true',
                'include_24hr_vol': 'true',
                'include_last_updated_at': 'true'
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Проверяем, что монета найдена
            if coin_id not in data:
                return None
            
            coin_data = data[coin_id]
            
            # Форматируем в удобный вид
            result = {
                'id': coin_id,
                'price_usd': coin_data.get('usd', 0),
                'price_change_24h': coin_data.get('usd_24h_change', 0),
                'market_cap': coin_data.get('usd_market_cap', 0),
                'volume_24h': coin_data.get('usd_24h_vol', 0),
                'last_updated': coin_data.get('last_updated_at', int(time.time()))
            }
            
            self.cache[cache_key] = {
                'data': result,
                'timestamp': time.time()
            }
            return result
        except Exception as e:
            print(f"Error fetching data for {coin_id}: {e}")
            return None
    
    def get_trending_coins(self) -> Optional[List[Dict]]:
        """Получить трендовые монеты"""
        cache_key = "trending"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            url = f"{self.coingecko_base}/search/trending"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            trending = data.get('coins', [])[:7]
            result = [{
                'name': coin['item']['name'],
                'symbol': coin['item']['symbol'],
                'market_cap_rank': coin['item'].get('market_cap_rank'),
                'price_btc': coin['item'].get('price_btc')
            } for coin in trending]
            
            self.cache[cache_key] = {
                'data': result,
                'timestamp': time.time()
            }
            return result
        except Exception as e:
            print(f"Error fetching trending coins: {e}")
            return None
    
    def get_market_overview(self) -> Optional[Dict]:
        """Получить общий обзор рынка"""
        cache_key = "market_overview"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            url = f"{self.coingecko_base}/global"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            global_data = data.get('data', {})
            result = {
                'total_market_cap_usd': global_data.get('total_market_cap', {}).get('usd'),
                'total_volume_usd': global_data.get('total_volume', {}).get('usd'),
                'market_cap_change_24h': global_data.get('market_cap_change_percentage_24h_usd'),
                'btc_dominance': global_data.get('market_cap_percentage', {}).get('btc'),
                'eth_dominance': global_data.get('market_cap_percentage', {}).get('eth'),
                'active_cryptocurrencies': global_data.get('active_cryptocurrencies')
            }
            
            self.cache[cache_key] = {
                'data': result,
                'timestamp': time.time()
            }
            return result
        except Exception as e:
            print(f"Error fetching market overview: {e}")
            return None
    
    def get_top_coins(self, limit: int = 10) -> Optional[List[Dict]]:
        """Получить топ монет по капитализации"""
        cache_key = f"top_coins_{limit}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            url = f"{self.coingecko_base}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': limit,
                'page': 1,
                'sparkline': False,
                'price_change_percentage': '24h'
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            result = [{
                'name': coin['name'],
                'symbol': coin['symbol'].upper(),
                'current_price': coin['current_price'],
                'market_cap': coin['market_cap'],
                'market_cap_rank': coin['market_cap_rank'],
                'price_change_24h': coin.get('price_change_percentage_24h'),
                'total_volume': coin['total_volume']
            } for coin in data]
            
            self.cache[cache_key] = {
                'data': result,
                'timestamp': time.time()
            }
            return result
        except Exception as e:
            print(f"Error fetching top coins: {e}")
            return None
    
    def search_coin(self, query: str) -> Optional[Dict]:
        """Поиск монеты по названию или символу с возвращением полной информации"""
        try:
            url = f"{self.coingecko_base}/search"
            params = {'query': query}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            coins = data.get('coins', [])
            if coins:
                # Возвращаем первый результат с полной информацией
                coin = coins[0]
                return {
                    'id': coin['id'],
                    'name': coin['name'],
                    'symbol': coin['symbol'].upper(),
                    'market_cap_rank': coin.get('market_cap_rank')
                }
            return None
        except Exception as e:
            print(f"Error searching coin: {e}")
            return None
    
    def search_multiple_coins(self, queries: List[str]) -> List[Dict]:
        """Поиск нескольких монет одновременно"""
        results = []
        for query in queries:
            coin_info = self.search_coin(query)
            if coin_info:
                results.append(coin_info)
        return results
    
    def get_coins_by_ids(self, coin_ids: List[str]) -> Optional[List[Dict]]:
        """Получить данные по нескольким монетам одновременно"""
        if not coin_ids:
            return None
            
        cache_key = f"coins_{'_'.join(sorted(coin_ids))}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            # CoinGecko позволяет запросить несколько монет через запятую
            ids_string = ','.join(coin_ids)
            url = f"{self.coingecko_base}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'ids': ids_string,
                'order': 'market_cap_desc',
                'sparkline': False,
                'price_change_percentage': '24h,7d'
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            result = [{
                'id': coin['id'],
                'name': coin['name'],
                'symbol': coin['symbol'].upper(),
                'current_price': coin['current_price'],
                'market_cap': coin['market_cap'],
                'market_cap_rank': coin['market_cap_rank'],
                'price_change_24h': coin.get('price_change_percentage_24h'),
                'price_change_7d': coin.get('price_change_percentage_7d_in_currency'),
                'total_volume': coin['total_volume'],
                'high_24h': coin.get('high_24h'),
                'low_24h': coin.get('low_24h')
            } for coin in data]
            
            self.cache[cache_key] = {
                'data': result,
                'timestamp': time.time()
            }
            return result
        except Exception as e:
            print(f"Error fetching coins by IDs: {e}")
            return None
    
    def get_coin_details(self, coin_id: str) -> Optional[Dict]:
        """Получить детальную информацию о монете"""
        cache_key = f"details_{coin_id}"
        
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        try:
            url = f"{self.coingecko_base}/coins/{coin_id}"
            params = {
                'localization': False,
                'tickers': False,
                'community_data': False,
                'developer_data': False
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            result = {
                'name': data['name'],
                'symbol': data['symbol'].upper(),
                'current_price': data['market_data']['current_price']['usd'],
                'market_cap': data['market_data']['market_cap']['usd'],
                'market_cap_rank': data['market_cap_rank'],
                'total_volume': data['market_data']['total_volume']['usd'],
                'high_24h': data['market_data']['high_24h']['usd'],
                'low_24h': data['market_data']['low_24h']['usd'],
                'price_change_24h': data['market_data']['price_change_percentage_24h'],
                'price_change_7d': data['market_data'].get('price_change_percentage_7d'),
                'price_change_30d': data['market_data'].get('price_change_percentage_30d'),
                'ath': data['market_data']['ath']['usd'],
                'ath_date': data['market_data']['ath_date']['usd'],
                'atl': data['market_data']['atl']['usd'],
                'atl_date': data['market_data']['atl_date']['usd']
            }
            
            self.cache[cache_key] = {
                'data': result,
                'timestamp': time.time()
            }
            return result
        except Exception as e:
            print(f"Error fetching coin details: {e}")
            return None
