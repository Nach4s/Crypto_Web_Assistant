import { TrendingUp, Crown, X, RefreshCw } from 'lucide-react'
import { useState } from 'react'

export default function Sidebar({ marketData, onClose }) {
  const [isRefreshing, setIsRefreshing] = useState(false)

  const handleRefresh = () => {
    setIsRefreshing(true)
    setTimeout(() => setIsRefreshing(false), 1000)
    window.location.reload()
  }

  return (
    <div className="w-80 bg-crypto-dark border-r border-gray-800 h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-800 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">Обзор рынка</h2>
        <div className="flex items-center gap-2">
          <button
            onClick={handleRefresh}
            className={`p-2 hover:bg-gray-800 rounded-lg transition-colors ${
              isRefreshing ? 'animate-spin' : ''
            }`}
          >
            <RefreshCw className="w-4 h-4 text-gray-400" />
          </button>
          {onClose && (
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors md:hidden"
            >
              <X className="w-4 h-4 text-gray-400" />
            </button>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* Trending Coins */}
        {marketData?.trending && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <TrendingUp className="w-4 h-4 text-orange-400" />
              <h3 className="text-sm font-semibold text-gray-300">Трендовые</h3>
            </div>
            <div className="space-y-2">
              {marketData.trending.map((coin, index) => (
                <div
                  key={index}
                  className="bg-gray-800/50 rounded-lg p-3 hover:bg-gray-800 transition-colors cursor-pointer"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-white">{coin.name}</p>
                      <p className="text-xs text-gray-400">{coin.symbol}</p>
                    </div>
                    {coin.market_cap_rank && (
                      <span className="text-xs text-gray-500">#{coin.market_cap_rank}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Top Coins */}
        {marketData?.top_coins && (
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Crown className="w-4 h-4 text-yellow-400" />
              <h3 className="text-sm font-semibold text-gray-300">Топ по капитализации</h3>
            </div>
            <div className="space-y-2">
              {marketData.top_coins.slice(0, 5).map((coin, index) => (
                <div
                  key={index}
                  className="bg-gray-800/50 rounded-lg p-3 hover:bg-gray-800 transition-colors cursor-pointer"
                >
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-500">#{coin.market_cap_rank}</span>
                      <p className="text-sm font-medium text-white">{coin.symbol}</p>
                    </div>
                    <p className="text-sm text-white font-semibold">
                      ${coin.current_price.toLocaleString()}
                    </p>
                  </div>
                  <div className="flex items-center justify-between">
                    <p className="text-xs text-gray-400">{coin.name}</p>
                    <span className={`text-xs font-medium ${
                      coin.price_change_24h >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {coin.price_change_24h >= 0 ? '+' : ''}
                      {coin.price_change_24h?.toFixed(2)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Market Stats */}
        {marketData?.market_overview && (
          <div>
            <h3 className="text-sm font-semibold text-gray-300 mb-3">Статистика</h3>
            <div className="space-y-3">
              <div className="bg-gray-800/50 rounded-lg p-3">
                <p className="text-xs text-gray-400 mb-1">Общая капитализация</p>
                <p className="text-lg font-bold text-white">
                  ${(marketData.market_overview.total_market_cap_usd / 1e12).toFixed(2)}T
                </p>
              </div>
              
              <div className="bg-gray-800/50 rounded-lg p-3">
                <p className="text-xs text-gray-400 mb-1">Объём 24ч</p>
                <p className="text-lg font-bold text-white">
                  ${(marketData.market_overview.total_volume_usd / 1e9).toFixed(2)}B
                </p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="bg-gray-800/50 rounded-lg p-3">
                  <p className="text-xs text-gray-400 mb-1">BTC</p>
                  <p className="text-sm font-bold text-orange-400">
                    {marketData.market_overview.btc_dominance?.toFixed(1)}%
                  </p>
                </div>
                <div className="bg-gray-800/50 rounded-lg p-3">
                  <p className="text-xs text-gray-400 mb-1">ETH</p>
                  <p className="text-sm font-bold text-blue-400">
                    {marketData.market_overview.eth_dominance?.toFixed(1)}%
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
