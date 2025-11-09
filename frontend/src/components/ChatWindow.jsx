import { useState, useRef, useEffect } from 'react'
import { Send, Loader2 } from 'lucide-react'
import Message from './Message'
import TypingIndicator from './TypingIndicator'

export default function ChatWindow({ sessionId }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: '📊 Привет! Я финансовый аналитик с доступом к **криптовалютам** и **фондовым активам**.\n\n**Примеры вопросов:**\n\n📈 Фондовый рынок:\n- Какая цена S&P 500?\n- Покажи Apple\n- Что с Tesla?\n\n💰 Криптовалюты:\n- Какая цена Bitcoin?\n- Покажи Toncoin\n- Что с Flare?\n\n🔍 Сравнение:\n- Сравни S&P 500 и Bitcoin\n- Что лучше: Apple или Ethereum?\n- Сравни SPY и QQQ\n\n📊 Анализ:\n- Обзор рынков\n- Какие активы растут?\n\n**Спрашивай о любых активах!**',
      timestamp: new Date()
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isLoading])

  useEffect(() => {
    adjustTextareaHeight()
  }, [input])

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = 'auto'
      textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px'
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage.content,
          session_id: sessionId,
          include_market_data: true
        })
      })

      if (!response.ok) {
        throw new Error('Failed to get response')
      }

      const data = await response.json()
      
      const assistantMessage = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error:', error)
      const errorMessage = {
        role: 'assistant',
        content: '😔 Извините, произошла ошибка при обработке вашего запроса. Попробуйте ещё раз.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div className="flex-1 flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-4 py-6 space-y-6">
          {messages.map((message, index) => (
            <Message key={index} message={message} />
          ))}
          {isLoading && <TypingIndicator />}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-800 bg-crypto-dark">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <form onSubmit={handleSubmit} className="relative">
            <div className="flex items-end gap-3 bg-gray-800 rounded-2xl p-3 focus-within:ring-2 focus-within:ring-crypto-accent transition-all">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Спросите о криптовалютах..."
                className="flex-1 bg-transparent text-white placeholder-gray-400 resize-none outline-none max-h-[200px] min-h-[24px]"
                rows={1}
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={!input.trim() || isLoading}
                className="flex-shrink-0 w-10 h-10 bg-crypto-accent hover:bg-crypto-accent-hover disabled:bg-gray-700 disabled:cursor-not-allowed rounded-xl flex items-center justify-center transition-colors"
              >
                {isLoading ? (
                  <Loader2 className="w-5 h-5 text-white animate-spin" />
                ) : (
                  <Send className="w-5 h-5 text-white" />
                )}
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-2 text-center">
              AI может делать ошибки. Проверяйте важную информацию.
            </p>
          </form>
        </div>
      </div>
    </div>
  )
}
