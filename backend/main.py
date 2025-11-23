"""
Main FastAPI application - точка входа backend
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
from dotenv import load_dotenv
import json
import base64

from data_layer import CryptoDataProvider
from stock_data_layer import StockDataProvider
from unified_data_layer import UnifiedDataProvider
from ai_layer import AIAssistant

# Загружаем переменные окружения
load_dotenv()

app = FastAPI(title="Crypto & Stock Chat Assistant API")

# CORS middleware для работы с фронтендом
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация провайдеров
data_provider = CryptoDataProvider()
stock_provider = StockDataProvider()
unified_provider = UnifiedDataProvider()

# Выбор AI провайдера из переменных окружения
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")  # "openai" или "groq"
ai_assistant = AIAssistant(provider=AI_PROVIDER)

# Хранилище истории диалогов (в продакшене использовать БД)
conversation_sessions: Dict[str, List[Dict]] = {}


# Pydantic модели для запросов/ответов
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    include_market_data: bool = True
    image_base64: Optional[str] = None  # base64 encoded image
    image_mime_type: Optional[str] = "image/jpeg"  # MIME type of image


class ChatResponse(BaseModel):
    response: str
    market_data: Optional[Dict] = None
    session_id: str


class MarketDataRequest(BaseModel):
    coin_id: Optional[str] = None
    include_trending: bool = True
    include_top_coins: bool = True
    top_coins_limit: int = 10


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Crypto Chat Assistant API",
        "ai_provider": AI_PROVIDER
    }


@app.get("/api/market/overview")
async def get_market_overview():
    """Получить общий обзор рынка"""
    try:
        overview = data_provider.get_market_overview()
        if overview is None:
            raise HTTPException(status_code=503, detail="Failed to fetch market data")
        return {"data": overview}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/market/trending")
async def get_trending():
    """Получить трендовые монеты"""
    try:
        trending = data_provider.get_trending_coins()
        if trending is None:
            raise HTTPException(status_code=503, detail="Failed to fetch trending data")
        return {"data": trending}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/market/top-coins")
async def get_top_coins(limit: int = 10):
    """Получить топ монет"""
    try:
        top_coins = data_provider.get_top_coins(limit=limit)
        if top_coins is None:
            raise HTTPException(status_code=503, detail="Failed to fetch top coins")
        return {"data": top_coins}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/market/coin/{coin_id}")
async def get_coin_details(coin_id: str):
    """Получить детали конкретной монеты"""
    try:
        details = data_provider.get_coin_details(coin_id)
        if details is None:
            raise HTTPException(status_code=404, detail=f"Coin {coin_id} not found")
        return {"data": details}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/market/search/{query}")
async def search_coin(query: str):
    """Поиск монеты по названию или символу"""
    try:
        coin_id = data_provider.search_coin(query)
        if coin_id is None:
            raise HTTPException(status_code=404, detail=f"Coin '{query}' not found")
        return {"coin_id": coin_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/market/data")
async def get_market_data(request: MarketDataRequest):
    """Получить комплексные рыночные данные"""
    try:
        result = {}
        
        # Общий обзор рынка
        result['market_overview'] = data_provider.get_market_overview()
        
        # Трендовые монеты
        if request.include_trending:
            result['trending'] = data_provider.get_trending_coins()
        
        # Топ монет
        if request.include_top_coins:
            result['top_coins'] = data_provider.get_top_coins(limit=request.top_coins_limit)
        
        # Детали конкретной монеты
        if request.coin_id:
            result['coin_details'] = data_provider.get_coin_details(request.coin_id)
        
        return {"data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _extract_coins_from_message(message: str) -> List[str]:
    """Умное извлечение названий монет из сообщения пользователя"""
    import re
    
    # Расширенный словарь популярных монет
    common_coins = {
        'bitcoin': 'bitcoin', 'btc': 'bitcoin',
        'ethereum': 'ethereum', 'eth': 'ethereum',
        'solana': 'solana', 'sol': 'solana',
        'cardano': 'cardano', 'ada': 'cardano',
        'ripple': 'ripple', 'xrp': 'ripple',
        'dogecoin': 'dogecoin', 'doge': 'dogecoin',
        'polkadot': 'polkadot', 'dot': 'polkadot',
        'avalanche': 'avalanche-2', 'avax': 'avalanche-2',
        'polygon': 'matic-network', 'matic': 'matic-network',
        'chainlink': 'chainlink', 'link': 'chainlink',
        'toncoin': 'the-open-network', 'ton': 'the-open-network',
        'zcash': 'zcash', 'zec': 'zcash',
        'monero': 'monero', 'xmr': 'monero',
        'litecoin': 'litecoin', 'ltc': 'litecoin',
        'binance': 'binancecoin', 'bnb': 'binancecoin',
        'tron': 'tron', 'trx': 'tron',
        'stellar': 'stellar', 'xlm': 'stellar',
        'cosmos': 'cosmos', 'atom': 'cosmos',
        'uniswap': 'uniswap', 'uni': 'uniswap',
        'filecoin': 'filecoin', 'fil': 'filecoin',
        'aptos': 'aptos', 'apt': 'aptos',
        'arbitrum': 'arbitrum', 'arb': 'arbitrum',
        'optimism': 'optimism', 'op': 'optimism',
        'near': 'near', 'near protocol': 'near',
        'shiba': 'shiba-inu', 'shib': 'shiba-inu',
        'pepe': 'pepe', 'meme': 'pepe',
        'flare': 'flare-networks', 'flr': 'flare-networks',
        'hedera': 'hedera-hashgraph', 'hbar': 'hedera-hashgraph',
        'algorand': 'algorand', 'algo': 'algorand',
        'vechain': 'vechain', 'vet': 'vechain',
        'internet computer': 'internet-computer', 'icp': 'internet-computer',
        'quant': 'quant-network', 'qnt': 'quant-network',
        'maker': 'maker', 'mkr': 'maker',
        'aave': 'aave', 'lend': 'aave',
    }
    
    message_lower = message.lower()
    found_coins = []
    
    # Ищем упоминания монет в сообщении
    for key, coin_id in common_coins.items():
        # Используем границы слов для точного поиска
        pattern = r'\b' + re.escape(key) + r'\b'
        if re.search(pattern, message_lower):
            if coin_id not in found_coins:
                found_coins.append(coin_id)
    
    # Если не нашли известные монеты, пробуем поискать через API
    if not found_coins:
        # Извлекаем потенциальные названия монет (слова длиной 3+ символа)
        words = re.findall(r'\b[a-zA-Zа-яА-Я]{3,}\b', message)
        for word in words[:3]:  # Проверяем максимум 3 слова
            coin_info = data_provider.search_coin(word)
            if coin_info and coin_info['id'] not in found_coins:
                found_coins.append(coin_info['id'])
    
    return found_coins


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatMessage):
    """Основной endpoint для чата"""
    try:
        # Получаем или создаём сессию
        session_id = request.session_id
        if session_id not in conversation_sessions:
            conversation_sessions[session_id] = []
        
        # Собираем рыночные данные (крипто + акции)
        market_data = {}
        if request.include_market_data:
            # Умное извлечение активов из сообщения (крипто + акции)
            assets = unified_provider.extract_assets_from_message(request.message)
            crypto_ids = assets.get('crypto', [])
            stock_symbols = assets.get('stocks', [])
            
            # Получаем унифицированные данные
            if crypto_ids or stock_symbols:
                unified_data = unified_provider.get_unified_data(crypto_ids, stock_symbols)
                market_data.update(unified_data)
            
            # Всегда включаем общий обзор рынка
            market_data['market_overview'] = data_provider.get_market_overview()
            market_data['trending'] = data_provider.get_trending_coins()
            market_data['top_coins'] = data_provider.get_top_coins(limit=10)
        
        # Получаем ответ от AI (с поддержкой изображений)
        response_text = await ai_assistant.get_response(
            user_message=request.message,
            market_data=market_data,
            conversation_history=conversation_sessions[session_id],
            image_base64=request.image_base64,
            image_mime_type=request.image_mime_type
        )
        
        # Сохраняем в историю
        user_content = request.message if request.message.strip() else ""
        if request.image_base64:
            if user_content:
                user_content = f"{user_content}\n[Изображение прикреплено]"
            else:
                user_content = "[Изображение прикреплено]"
        
        conversation_sessions[session_id].append({
            "role": "user",
            "content": user_content
        })
        conversation_sessions[session_id].append({
            "role": "assistant",
            "content": response_text
        })
        
        # Ограничиваем размер истории
        if len(conversation_sessions[session_id]) > 20:
            conversation_sessions[session_id] = conversation_sessions[session_id][-20:]
        
        return ChatResponse(
            response=response_text,
            market_data=market_data if request.include_market_data else None,
            session_id=session_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/stream")
async def chat_stream(request: ChatMessage):
    """Стриминговый endpoint для чата (как у ChatGPT)"""
    try:
        session_id = request.session_id
        if session_id not in conversation_sessions:
            conversation_sessions[session_id] = []
        
        # Собираем рыночные данные (крипто + акции)
        market_data = {}
        if request.include_market_data:
            # Умное извлечение активов из сообщения (крипто + акции)
            assets = unified_provider.extract_assets_from_message(request.message)
            crypto_ids = assets.get('crypto', [])
            stock_symbols = assets.get('stocks', [])
            
            # Получаем унифицированные данные
            if crypto_ids or stock_symbols:
                unified_data = unified_provider.get_unified_data(crypto_ids, stock_symbols)
                market_data.update(unified_data)
            
            market_data['market_overview'] = data_provider.get_market_overview()
            market_data['trending'] = data_provider.get_trending_coins()
            market_data['top_coins'] = data_provider.get_top_coins(limit=10)
        
        # Сохраняем вопрос пользователя
        user_content = request.message if request.message.strip() else ""
        if request.image_base64:
            if user_content:
                user_content = f"{user_content}\n[Изображение прикреплено]"
            else:
                user_content = "[Изображение прикреплено]"
        
        conversation_sessions[session_id].append({
            "role": "user",
            "content": user_content
        })
        
        async def generate():
            full_response = ""
            async for chunk in ai_assistant.get_streaming_response(
                user_message=request.message,
                market_data=market_data,
                conversation_history=conversation_sessions[session_id][:-1],
                image_base64=request.image_base64,
                image_mime_type=request.image_mime_type
            ):
                full_response += chunk
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            # Сохраняем полный ответ в историю
            conversation_sessions[session_id].append({
                "role": "assistant",
                "content": full_response
            })
            
            # Ограничиваем размер истории
            if len(conversation_sessions[session_id]) > 20:
                conversation_sessions[session_id] = conversation_sessions[session_id][-20:]
            
            yield f"data: {json.dumps({'done': True})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/chat/session/{session_id}")
async def clear_session(session_id: str):
    """Очистить историю сессии"""
    if session_id in conversation_sessions:
        del conversation_sessions[session_id]
        return {"message": "Session cleared"}
    return {"message": "Session not found"}


@app.get("/api/chat/history/{session_id}")
async def get_history(session_id: str):
    """Получить историю диалога"""
    if session_id in conversation_sessions:
        return {"history": conversation_sessions[session_id]}
    return {"history": []}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
