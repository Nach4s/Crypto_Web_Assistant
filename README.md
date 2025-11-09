# 🚀 Crypto & Stock Chat Assistant

Умный AI-ассистент для анализа **криптовалютного** и **фондового** рынков с современным веб-интерфейсом в стиле ChatGPT.

## ✨ Возможности

- 💬 **Интерактивный чат** - интерфейс как у ChatGPT
- 📈 **Фондовые активы** - акции, ETF, индексы (S&P 500, Apple, Tesla через Yahoo Finance)
- 🌐 **Любые криптовалюты** - тысячи монет (Bitcoin, Toncoin, Zcash через CoinGecko)
- 📊 **Унифицированные данные** - объединение крипто и фондовых активов в одном JSON
- 🤖 **Умный AI-анализ** - гибкие аналитические ответы (OpenAI GPT-4 / Groq Llama 3)
- 🎯 **Автопоиск активов** - умное извлечение монет и акций из вопроса
- 🔍 **Сравнительный анализ** - сравнение крипто vs акции, индексов, ETF
- 📉 **Рыночная статистика** - топ монет, трендовые криптовалюты, индексы
- 🎨 **Современный UI** - React + TailwindCSS с темной темой
- ⚡ **Быстрые ответы** - кэширование данных и оптимизированные запросы

## 🏗️ Архитектура

```
crypto-web-assistant/
├── backend/                    # FastAPI сервер
│   ├── main.py                # Основной API endpoint
│   ├── data_layer.py          # CoinGecko (криптовалюты)
│   ├── stock_data_layer.py    # Yahoo Finance (акции, ETF, индексы)
│   ├── unified_data_layer.py  # Объединение данных
│   ├── ai_layer.py            # AI модели (OpenAI/Groq)
│   └── requirements.txt
│
├── frontend/            # React + Vite приложение
│   ├── src/
│   │   ├── components/  # UI компоненты
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
│
├── .env.example         # Пример конфигурации
└── README.md
```

## 🚀 Быстрый старт

### 1. Клонирование и настройка

```bash
cd Crypto_Web_Assistant
```

### 2. Настройка Backend

```bash
cd backend

# Создать виртуальное окружение
python -m venv venv

# Активировать (Windows)
venv\Scripts\activate

# Активировать (Linux/Mac)
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt
```

### 3. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
# Выберите AI провайдера
AI_PROVIDER=openai  # или "groq"

# OpenAI API Key (получить на https://platform.openai.com/)
OPENAI_API_KEY=sk-your-key-here

# Или Groq API Key (получить на https://console.groq.com/)
GROQ_API_KEY=your-groq-key-here
```

### 4. Запуск Backend

```bash
venv\Scripts\activate
cd backend
python main.py
```

Backend запустится на `http://localhost:8000`

### 5. Настройка Frontend

Откройте новый терминал:

```bash
cd frontend

# Установить зависимости
npm install

# Запустить dev сервер
npm run dev
```

Frontend запустится на `http://localhost:3000`

## 🔑 Получение API ключей

### OpenAI API Key

1. Зарегистрируйтесь на [OpenAI Platform](https://platform.openai.com/)
2. Перейдите в раздел API Keys
3. Создайте новый ключ
4. Добавьте его в `.env` файл

### Groq API Key (альтернатива)

1. Зарегистрируйтесь на [Groq Console](https://console.groq.com/)
2. Создайте API ключ
3. Добавьте его в `.env` файл
4. Установите `AI_PROVIDER=groq`

## 📡 API Endpoints

### Backend API

- `GET /` - Health check
- `GET /api/market/overview` - Общий обзор рынка
- `GET /api/market/trending` - Трендовые монеты
- `GET /api/market/top-coins` - Топ монет по капитализации
- `GET /api/market/coin/{coin_id}` - Детали конкретной монеты
- `POST /api/chat` - Отправить сообщение в чат
- `POST /api/chat/stream` - Стриминговый чат (как у ChatGPT)

## 🎨 Технологический стек

### Backend
- **FastAPI** - современный Python веб-фреймворк
- **OpenAI API** - GPT-4/5 модели
- **Groq API** - Llama 3 модели (альтернатива)
- **CoinGecko API** - данные о криптовалютах
- **Binance API** - дополнительные рыночные данные

### Frontend
- **React 18** - UI библиотека
- **Vite** - сборщик и dev сервер
- **TailwindCSS** - utility-first CSS фреймворк
- **Lucide React** - иконки
- **React Markdown** - рендеринг markdown ответов

## 💡 Примеры вопросов

### 📈 Фондовый рынок:
- "Какая цена S&P 500?" - индекс S&P 500
- "Покажи Apple" - акция AAPL
- "Что с Tesla?" - анализ TSLA
- "Сравни SPY и QQQ" - ETF сравнение

### 💰 Криптовалюты:
- "Какая цена Bitcoin?" - данные по BTC
- "Покажи Toncoin" - информация о TON
- "Что с Flare?" - анализ FLR
- "Сравни Ethereum и Solana"

### 🔍 Кросс-анализ:
- "Сравни S&P 500 и Bitcoin"
- "Что лучше: Apple или Ethereum?"
- "Обзор рынков" - крипто + фондовый

### 📊 Общий анализ:
- "Какие активы растут?"
- "Покажи топ 5 по динамике"
- "Тренды на рынках"

**Поддерживаются тысячи активов!** Спрашивайте о любых криптовалютах, акциях, ETF и индексах.

## 🔧 Разработка

### Backend разработка

```bash
cd backend
# Запуск с автоперезагрузкой
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend разработка

```bash
cd frontend
npm run dev
```

### Сборка для продакшена

```bash
# Frontend
cd frontend
npm run build

# Backend
cd backend
# Использовать gunicorn или uvicorn с production настройками
```

## 🌟 Будущие улучшения

- [ ] Сохранение истории диалогов в БД
- [ ] Авторизация пользователей
- [ ] Графики цен (Chart.js / Recharts)
- [ ] Уведомления о важных событиях
- [ ] Мультиязычность
- [ ] Голосовой ввод
- [ ] Экспорт диалогов
- [ ] Персональные настройки

## 📝 Лицензия

MIT License - свободно используйте для своих проектов!

## 🤝 Вклад

Приветствуются pull requests и issues!

## ⚠️ Дисклеймер

Этот ассистент предоставляет информацию и анализ, но НЕ является финансовым советом. Всегда проводите собственное исследование перед инвестициями.

---

Сделано с ❤️ для крипто-сообщества
