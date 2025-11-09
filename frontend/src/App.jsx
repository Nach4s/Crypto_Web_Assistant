import { useState, useEffect } from 'react'
import ChatWindow from './components/ChatWindow'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import { Menu, X } from 'lucide-react'

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [sessionId] = useState(() => `session_${Date.now()}`)
  const [marketData, setMarketData] = useState(null)

  // Загружаем рыночные данные при старте
  useEffect(() => {
    fetchMarketData()
    // Обновляем каждые 60 секунд
    const interval = setInterval(fetchMarketData, 60000)
    return () => clearInterval(interval)
  }, [])

  const fetchMarketData = async () => {
    try {
      const response = await fetch('/api/market/data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          include_trending: true,
          include_top_coins: true,
          top_coins_limit: 10
        })
      })
      const data = await response.json()
      setMarketData(data.data)
    } catch (error) {
      console.error('Error fetching market data:', error)
    }
  }

  return (
    <div className="flex h-screen bg-crypto-darker overflow-hidden">
      {/* Sidebar для десктопа */}
      <div className="hidden md:block">
        <Sidebar marketData={marketData} />
      </div>

      {/* Мобильный Sidebar */}
      {sidebarOpen && (
        <>
          <div 
            className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
            onClick={() => setSidebarOpen(false)}
          />
          <div className="fixed inset-y-0 left-0 z-50 md:hidden">
            <Sidebar marketData={marketData} onClose={() => setSidebarOpen(false)} />
          </div>
        </>
      )}

      {/* Основной контент */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <Header 
          onMenuClick={() => setSidebarOpen(!sidebarOpen)}
          marketData={marketData}
        />

        {/* Chat Window */}
        <ChatWindow sessionId={sessionId} />
      </div>
    </div>
  )
}

export default App
