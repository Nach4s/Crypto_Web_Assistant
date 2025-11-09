import { Menu, TrendingUp, TrendingDown } from 'lucide-react'

export default function Header({ onMenuClick, marketData }) {
  const overview = marketData?.market_overview

  return (
    <header className="bg-crypto-dark border-b border-gray-800 px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuClick}
          className="md:hidden p-2 hover:bg-gray-800 rounded-lg transition-colors"
        >
          <Menu className="w-5 h-5" />
        </button>
        
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">₿</span>
          </div>
          <div>
            <h1 className="text-lg font-bold text-white">Crypto Assistant</h1>
            <p className="text-xs text-gray-400 hidden sm:block">AI-помощник по крипторынку</p>
          </div>
        </div>
      </div>

      {overview && (
        <div className="hidden lg:flex items-center gap-6 text-sm">
          <div className="flex items-center gap-2">
            <span className="text-gray-400">Капитализация:</span>
            <span className="text-white font-semibold">
              ${(overview.total_market_cap_usd / 1e12).toFixed(2)}T
            </span>
          </div>
          
          <div className="flex items-center gap-2">
            <span className="text-gray-400">24ч:</span>
            <span className={`flex items-center gap-1 font-semibold ${
              overview.market_cap_change_24h >= 0 ? 'text-green-400' : 'text-red-400'
            }`}>
              {overview.market_cap_change_24h >= 0 ? (
                <TrendingUp className="w-4 h-4" />
              ) : (
                <TrendingDown className="w-4 h-4" />
              )}
              {Math.abs(overview.market_cap_change_24h).toFixed(2)}%
            </span>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-gray-400">BTC:</span>
            <span className="text-orange-400 font-semibold">
              {overview.btc_dominance?.toFixed(1)}%
            </span>
          </div>
        </div>
      )}
    </header>
  )
}
