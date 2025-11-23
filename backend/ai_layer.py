"""
AI Layer - интеграция с OpenAI и Groq для генерации ответов
"""
import os
from typing import List, Dict, Optional
from openai import OpenAI
from groq import Groq
import json

class AIAssistant:
    def __init__(self, provider: str = "openai"):
        """
        provider: "openai" или "groq"
        """
        self.provider = provider
        
        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            self.client = OpenAI(api_key=api_key)
            self.model = "gpt-4o-mini"
        elif provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY not found in environment")
            self.client = Groq(api_key=api_key)
            self.model = "llama-3.1-70b-versatile"
        else:
            raise ValueError(f"Unknown provider: {provider}")
        
        self.system_prompt = """Ты — эксперт по финансовым рынкам и аналитик. Ты работаешь с **криптовалютами** и **фондовыми активами** (акции, ETF, индексы). Твоя задача — отвечать на вопросы пользователя **исключительно на основе актуальных данных, которые тебе передают**.

КРИТИЧЕСКИ ВАЖНО:
- Используй ТОЛЬКО данные из переданного JSON
- ВСЕГДА используй цены в USD (долларах), НЕ в BTC
- Если есть раздел "crypto" или "stocks" с полными данными - используй ИХ в первую очередь
- Раздел "trending" содержит только цены в BTC - используй его ТОЛЬКО если нет данных в "crypto"
- Если актив (монета или акция) есть в JSON, ВСЕГДА указывай его цену в USD и изменение за 24 часа
- НИКОГДА не пиши «данные отсутствуют» или «информация недоступна», если актив есть в JSON
- Если данных нет в JSON, честно скажи об этом, но не выдумывай цифры
- Различай криптовалюты и фондовые активы в своих ответах

Правила:
1. Используй только те данные, которые переданы в JSON (цены, капитализация, изменение за 24 часа, объёмы)
2. Отвечай **не шаблонно**, формируя полноценный аналитический обзор конкретно под запрос пользователя
3. Сравнивай активы по динамике, росту/падению, активности, объёму торгов и трендам
4. Выделяй топ-3–5 наиболее интересных или динамичных активов для анализа
5. Всегда включай в ответ **актуальные цены всех запрашиваемых активов**
6. НЕ давай финансовых советов и не используй общие предупреждения (не пишешь «не инвестируйте больше, чем можете потерять»)
7. Структура ответа должна быть гибкой и ориентированной на **аналитическую суть**:
   - Цифры, рост/падение, динамика
   - Тренды и активность
   - Сопоставления между активами (крипто vs акции, если уместно)
8. Подстраивай логику ответа под конкретный вопрос пользователя
9. Форматируй ответы красиво, используй эмодзи для наглядности
10. Отвечай на русском языке

Фокус на фактах, цифрах и динамике. Адаптируй структуру ответа под суть вопроса."""
    
    def _format_market_data(self, market_data: Dict) -> str:
        """Форматирование рыночных данных для промпта (крипто + акции)"""
        formatted = []
        
        # Фондовые активы (приоритет, если есть)
        if 'stocks' in market_data and market_data['stocks']:
            formatted.append("📈 Фондовые активы (акции, ETF, индексы):")
            for symbol, data in market_data['stocks'].items():
                change = data.get('change_24h', 0)
                emoji = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
                asset_type = data.get('type', 'Stock')
                name = data.get('name', symbol)
                formatted.append(
                    f"{emoji} {symbol} ({asset_type}) - {name}: "
                    f"${data['price']:,.2f} ({change:+.2f}% за 24ч)"
                )
            formatted.append("")
        
        # Криптовалюты
        if 'crypto' in market_data and market_data['crypto']:
            formatted.append("💰 Криптовалюты:")
            for coin_id, data in market_data['crypto'].items():
                change = data.get('change_24h', 0)
                emoji = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
                formatted.append(
                    f"{emoji} {coin_id.upper()}: "
                    f"${data['price']:,.4f} ({change:+.2f}% за 24ч)"
                )
            formatted.append("")
        
        if 'market_overview' in market_data and market_data['market_overview']:
            overview = market_data['market_overview']
            formatted.append("📊 Общий обзор рынка:")
            formatted.append(f"- Общая капитализация: ${overview.get('total_market_cap_usd', 0):,.0f}")
            formatted.append(f"- Изменение за 24ч: {overview.get('market_cap_change_24h', 0):.2f}%")
            formatted.append(f"- Доминация BTC: {overview.get('btc_dominance', 0):.2f}%")
            formatted.append(f"- Доминация ETH: {overview.get('eth_dominance', 0):.2f}%")
            formatted.append("")
        
        if 'top_coins' in market_data and market_data['top_coins']:
            formatted.append("🏆 Топ монет по капитализации:")
            for coin in market_data['top_coins']:
                change = coin.get('price_change_24h', 0)
                emoji = "🟢" if change > 0 else "🔴"
                formatted.append(
                    f"{emoji} #{coin['market_cap_rank']} {coin['name']} ({coin['symbol']}): "
                    f"${coin['current_price']:,.2f} ({change:+.2f}% за 24ч), "
                    f"Капитализация: ${coin['market_cap']:,.0f}, "
                    f"Объём: ${coin['total_volume']:,.0f}"
                )
            formatted.append("")
        
        if 'trending' in market_data and market_data['trending']:
            formatted.append("🔥 Трендовые монеты (сейчас популярны):")
            for coin in market_data['trending']:
                rank_info = f"Ранг: #{coin['market_cap_rank']}" if coin.get('market_cap_rank') else "Новая монета"
                price_info = f", Цена в BTC: {coin['price_btc']}" if coin.get('price_btc') else ""
                formatted.append(f"- {coin['name']} ({coin['symbol']}) - {rank_info}{price_info}")
            formatted.append("")
        
        # Данные по упомянутым монетам (приоритет!)
        if 'mentioned_coins' in market_data and market_data['mentioned_coins']:
            formatted.append("🎯 Упомянутые монеты (актуальные данные):")
            for coin in market_data['mentioned_coins']:
                change = coin.get('price_change_24h', 0)
                emoji = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
                change_7d = coin.get('price_change_7d', 0)
                formatted.append(
                    f"{emoji} {coin['name']} ({coin['symbol']}): "
                    f"${coin['current_price']:,.2f} "
                    f"({change:+.2f}% за 24ч, {change_7d:+.2f}% за 7д), "
                    f"Ранг: #{coin['market_cap_rank']}, "
                    f"Капитализация: ${coin['market_cap']:,.0f}, "
                    f"Объём: ${coin['total_volume']:,.0f}"
                )
            formatted.append("")
        
        # Упрощенные данные монет (если основные данные недоступны)
        if 'mentioned_coins_simple' in market_data and market_data['mentioned_coins_simple']:
            if 'mentioned_coins' not in market_data or not market_data['mentioned_coins']:
                formatted.append("🎯 Запрошенные монеты (актуальные цены):")
                for coin in market_data['mentioned_coins_simple']:
                    change = coin.get('price_change_24h', 0)
                    emoji = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
                    formatted.append(
                        f"{emoji} {coin['id'].upper()}: "
                        f"${coin['price_usd']:,.4f} "
                        f"({change:+.2f}% за 24ч), "
                        f"Капитализация: ${coin['market_cap']:,.0f}, "
                        f"Объём 24ч: ${coin['volume_24h']:,.0f}"
                    )
                formatted.append("")
        
        if 'coin_details' in market_data and market_data['coin_details']:
            details = market_data['coin_details']
            formatted.append(f"💎 Детали {details['name']} ({details['symbol']}):")
            formatted.append(f"- Цена: ${details['current_price']:,.2f}")
            formatted.append(f"- Капитализация: ${details['market_cap']:,.0f}")
            formatted.append(f"- Объём 24ч: ${details['total_volume']:,.0f}")
            formatted.append(f"- Изменение 24ч: {details.get('price_change_24h', 0):+.2f}%")
            if details.get('price_change_7d'):
                formatted.append(f"- Изменение 7д: {details['price_change_7d']:+.2f}%")
            if details.get('price_change_30d'):
                formatted.append(f"- Изменение 30д: {details['price_change_30d']:+.2f}%")
            formatted.append(f"- ATH: ${details['ath']:,.2f}")
            formatted.append(f"- ATL: ${details['atl']:,.2f}")
            formatted.append("")
        
        return "\n".join(formatted)
    
    async def get_response(
        self, 
        user_message: str, 
        market_data: Dict,
        conversation_history: Optional[List[Dict]] = None,
        image_base64: Optional[str] = None,
        image_mime_type: Optional[str] = "image/jpeg"
    ) -> str:
        """Получить ответ от AI модели"""
        try:
            # Форматируем рыночные данные
            market_context = self._format_market_data(market_data)
            
            # Формируем сообщения
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Добавляем историю диалога если есть
            if conversation_history:
                messages.extend(conversation_history[-10:])  # последние 10 сообщений
            
            # Если есть изображение, используем специальный промпт для изображений
            if image_base64:
                image_prompt = """ТВОИ ПРАВИЛА РАБОТЫ С ИЗОБРАЖЕНИЯМИ:

Если пользователь прикрепил изображение:

1. Определи, что на нём
2. Опиши видимую информацию
3. Выдели ключевые элементы
4. Сделай короткий вывод

Не придумывай того, чего не видно.
Если изображение нечеткое — запроси лучшее.

Если на изображении график:
- опиши тренд (вверх/вниз/флэт)
- уровни поддержки/сопротивления
- волатильность
- объемы (если видно)
- вероятное направление движения (без процентов и рекомендаций)

НЕ использовать:
- реальные названия активов, если их не видно
- финансовые советы
- прогнозы прибыли

Если изображения нет — работай как обычный текстовый ассистент."""
                
                # Формируем сообщение с изображением
                user_content = []
                
                # Формируем текстовую часть (всегда добавляем, даже если нет текста от пользователя)
                text_prompt = f"""{image_prompt}

Проанализируй прикрепленное изображение согласно правилам выше."""
                
                if user_message.strip():
                    text_prompt = f"""Актуальные данные о рынке (JSON):

{market_context}

Вопрос пользователя: "{user_message}"

{image_prompt}

Проанализируй прикрепленное изображение согласно правилам выше."""
                
                user_content.append({
                    "type": "text",
                    "text": text_prompt
                })
                
                # Добавляем изображение
                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{image_mime_type};base64,{image_base64}"
                    }
                })
                
                messages.append({
                    "role": "user",
                    "content": user_content
                })
                
                # Используем vision модель для OpenAI
                if self.provider == "openai":
                    response = self.client.chat.completions.create(
                        model="gpt-4o-mini",  # Используем модель с поддержкой vision
                        messages=messages,
                        temperature=0.7,
                        max_tokens=1500
                    )
                    return response.choices[0].message.content
                elif self.provider == "groq":
                    # Groq пока не поддерживает vision, возвращаем сообщение
                    return "Извините, обработка изображений пока доступна только с OpenAI. Пожалуйста, используйте OpenAI провайдер."
            else:
                # Обычный текстовый запрос
                context_message = f"""Актуальные данные о рынке (JSON):

{market_context}

Вопрос пользователя: "{user_message}"

Используй только данные из JSON. Дай аналитический, конкретный ответ, включая актуальные цены всех запрашиваемых монет и динамику их изменения. Не используй шаблонные блоки, формируй ответ под суть вопроса."""
                
                messages.append({"role": "user", "content": context_message})
                
                # Вызываем модель
                if self.provider == "openai":
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=0.7,
                        max_tokens=1500
                    )
                    return response.choices[0].message.content
                
                elif self.provider == "groq":
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=0.7,
                        max_tokens=1500
                    )
                    return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error getting AI response: {e}")
            return f"Извините, произошла ошибка при обработке запроса: {str(e)}"
    
    async def get_streaming_response(
        self,
        user_message: str,
        market_data: Dict,
        conversation_history: Optional[List[Dict]] = None,
        image_base64: Optional[str] = None,
        image_mime_type: Optional[str] = "image/jpeg"
    ):
        """Получить стриминговый ответ от AI модели"""
        try:
            market_context = self._format_market_data(market_data)
            
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            if conversation_history:
                messages.extend(conversation_history[-10:])
            
            # Если есть изображение
            if image_base64:
                image_prompt = """ТВОИ ПРАВИЛА РАБОТЫ С ИЗОБРАЖЕНИЯМИ:

Если пользователь прикрепил изображение:

1. Определи, что на нём
2. Опиши видимую информацию
3. Выдели ключевые элементы
4. Сделай короткий вывод

Не придумывай того, чего не видно.
Если изображение нечеткое — запроси лучшее.

Если на изображении график:
- опиши тренд (вверх/вниз/флэт)
- уровни поддержки/сопротивления
- волатильность
- объемы (если видно)
- вероятное направление движения (без процентов и рекомендаций)

НЕ использовать:
- реальные названия активов, если их не видно
- финансовые советы
- прогнозы прибыли

Если изображения нет — работай как обычный текстовый ассистент."""
                
                user_content = []
                
                # Формируем текстовую часть (всегда добавляем, даже если нет текста от пользователя)
                text_prompt = f"""{image_prompt}

Проанализируй прикрепленное изображение согласно правилам выше."""
                
                if user_message.strip():
                    text_prompt = f"""Актуальные данные о рынке (JSON):

{market_context}

Вопрос пользователя: "{user_message}"

{image_prompt}

Проанализируй прикрепленное изображение согласно правилам выше."""
                
                user_content.append({
                    "type": "text",
                    "text": text_prompt
                })
                
                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{image_mime_type};base64,{image_base64}"
                    }
                })
                
                messages.append({
                    "role": "user",
                    "content": user_content
                })
                
                if self.provider == "openai":
                    stream = self.client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages,
                        temperature=0.7,
                        max_tokens=1500,
                        stream=True
                    )
                    
                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            yield chunk.choices[0].delta.content
                elif self.provider == "groq":
                    yield "Извините, обработка изображений пока доступна только с OpenAI."
            else:
                # Обычный текстовый запрос
                context_message = f"""Актуальные данные о рынке (JSON):

{market_context}

Вопрос пользователя: "{user_message}"

Используй только данные из JSON. Дай аналитический, конкретный ответ, включая актуальные цены всех запрашиваемых монет и динамику их изменения. Не используй шаблонные блоки, формируй ответ под суть вопроса."""
                
                messages.append({"role": "user", "content": context_message})
                
                if self.provider == "openai":
                    stream = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=0.7,
                        max_tokens=1500,
                        stream=True
                    )
                    
                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            yield chunk.choices[0].delta.content
                
                elif self.provider == "groq":
                    stream = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=0.7,
                        max_tokens=1500,
                        stream=True
                    )
                    
                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            yield chunk.choices[0].delta.content
                        
        except Exception as e:
            print(f"Error in streaming response: {e}")
            yield f"Извините, произошла ошибка: {str(e)}"
