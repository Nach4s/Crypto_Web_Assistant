"""
Unified Data Layer - объединение данных из CoinGecko и Yahoo Finance
"""
from typing import Dict, List, Optional
from data_layer import CryptoDataProvider
from stock_data_layer import StockDataProvider

class UnifiedDataProvider:
    def __init__(self):
        self.crypto_provider = CryptoDataProvider()
        self.stock_provider = StockDataProvider()
    
    def get_unified_data(self, crypto_ids: List[str] = None, stock_symbols: List[str] = None) -> Dict:
        """
        Получить унифицированные данные по криптовалютам и акциям
        
        Returns:
        {
            "stocks": {
                "^GSPC": {"price": 6045.26, "change_24h": 0.75, "name": "S&P 500", ...},
                "SPY": {"price": 670.97, "change_24h": 0.11, "name": "SPDR S&P 500 ETF", ...}
            },
            "crypto": {
                "bitcoin": {"price": 67456.50, "change_24h": -0.88, "name": "Bitcoin", ...},
                "toncoin": {"price": 2.11, "change_24h": -0.45, "name": "Toncoin", ...}
            }
        }
        """
        result = {
            "stocks": {},
            "crypto": {}
        }
        
        # Получаем данные по криптовалютам
        if crypto_ids:
            for coin_id in crypto_ids:
                coin_data = self.crypto_provider.get_any_coin_data(coin_id)
                if coin_data:
                    result["crypto"][coin_id] = {
                        "price": coin_data.get('price_usd', 0),
                        "change_24h": coin_data.get('price_change_24h', 0),
                        "market_cap": coin_data.get('market_cap', 0),
                        "volume_24h": coin_data.get('volume_24h', 0),
                        "type": "crypto"
                    }
        
        # Получаем данные по акциям
        if stock_symbols:
            for symbol in stock_symbols:
                stock_data = self.stock_provider.get_stock_price(symbol)
                if stock_data:
                    result["stocks"][symbol] = {
                        "price": stock_data.get('price', 0),
                        "change_24h": stock_data.get('change_24h', 0),
                        "name": stock_data.get('name', symbol),
                        "market_cap": stock_data.get('market_cap', 0),
                        "volume": stock_data.get('volume', 0),
                        "type": stock_data.get('type', 'stock')
                    }
        
        return result
    
    def get_market_overview(self) -> Dict:
        """Получить общий обзор рынков (крипто + фондовый)"""
        result = {
            "crypto_overview": self.crypto_provider.get_market_overview(),
            "stock_indices": self.stock_provider.get_market_indices(),
            "popular_stocks": {},
            "trending_crypto": self.crypto_provider.get_trending_coins(),
            "top_crypto": self.crypto_provider.get_top_coins(limit=5)
        }
        
        # Добавляем несколько популярных акций
        popular = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'TSLA']
        for symbol in popular:
            data = self.stock_provider.get_stock_price(symbol)
            if data:
                result["popular_stocks"][symbol] = data
        
        return result
    
    def search_asset(self, query: str) -> Optional[Dict]:
        """
        Поиск актива (крипто или акция)
        Возвращает тип актива и его ID/символ
        """
        # Сначала пробуем найти как акцию (если содержит буквы в верхнем регистре или ^)
        if query.isupper() or query.startswith('^') or len(query) <= 5:
            stock_info = self.stock_provider.search_stock(query)
            if stock_info:
                return {
                    'type': 'stock',
                    'symbol': stock_info['symbol'],
                    'name': stock_info.get('name', query),
                    'asset_type': stock_info.get('type', 'Stock')
                }
        
        # Пробуем найти как криптовалюту
        crypto_info = self.crypto_provider.search_coin(query)
        if crypto_info:
            return {
                'type': 'crypto',
                'id': crypto_info['id'],
                'name': crypto_info['name'],
                'symbol': crypto_info['symbol']
            }
        
        return None
    
    def extract_assets_from_message(self, message: str) -> Dict[str, List[str]]:
        """
        Извлечь упоминания активов из сообщения
        
        Returns:
        {
            "crypto": ["bitcoin", "ethereum"],
            "stocks": ["AAPL", "^GSPC"]
        }
        """
        import re
        
        result = {
            "crypto": [],
            "stocks": []
        }
        
        # Словарь популярных акций и индексов
        stock_keywords = {
            's&p 500': '^GSPC', 's&p': '^GSPC', 'sp500': '^GSPC', 
            's p 500': '^GSPC', 'sp 500': '^GSPC',  # Варианты без &
            'spy': 'SPY',
            'dow jones': '^DJI', 'dow': '^DJI', 'nasdaq': '^IXIC',
            'apple': 'AAPL', 'aapl': 'AAPL',
            'microsoft': 'MSFT', 'msft': 'MSFT',
            'google': 'GOOGL', 'googl': 'GOOGL',
            'amazon': 'AMZN', 'amzn': 'AMZN',
            'tesla': 'TSLA', 'tsla': 'TSLA',
            'nvidia': 'NVDA', 'nvda': 'NVDA',
            'meta': 'META',
            'qqq': 'QQQ', 'voo': 'VOO'
        }
        
        # Словарь криптовалют
        crypto_keywords = {
            'bitcoin': 'bitcoin', 'btc': 'bitcoin',
            'ethereum': 'ethereum', 'eth': 'ethereum',
            'solana': 'solana', 'sol': 'solana',
            'toncoin': 'the-open-network', 'ton': 'the-open-network',
            'flare': 'flare-networks', 'flr': 'flare-networks',
            'cardano': 'cardano', 'ada': 'cardano',
            'ripple': 'ripple', 'xrp': 'ripple',
            'firo': 'zcoin', 'firo coin': 'zcoin',
            'worldcoin': 'worldcoin-wld', 'wld': 'worldcoin-wld',
        }
        
        message_lower = message.lower()
        
        # Ищем акции (используем простой поиск подстроки для фраз с &)
        for key, symbol in stock_keywords.items():
            # Для фраз с & используем простой поиск
            if '&' in key or ' ' in key:
                if key in message_lower:
                    if symbol not in result["stocks"]:
                        result["stocks"].append(symbol)
            else:
                # Для простых слов используем word boundary
                pattern = r'\b' + re.escape(key) + r'\b'
                if re.search(pattern, message_lower):
                    if symbol not in result["stocks"]:
                        result["stocks"].append(symbol)
        
        # Ищем криптовалюты
        for key, coin_id in crypto_keywords.items():
            pattern = r'\b' + re.escape(key) + r'\b'
            if re.search(pattern, message_lower):
                if coin_id not in result["crypto"]:
                    result["crypto"].append(coin_id)
        
        # Если ничего не нашли, пробуем автопоиск
        if not result["stocks"] and not result["crypto"]:
            words = re.findall(r'\b[A-Z]{2,5}\b', message)  # Тикеры акций (заглавные буквы)
            for word in words[:2]:
                asset_info = self.search_asset(word)
                if asset_info:
                    if asset_info['type'] == 'stock':
                        result["stocks"].append(asset_info['symbol'])
                    else:
                        result["crypto"].append(asset_info['id'])
        
        return result
