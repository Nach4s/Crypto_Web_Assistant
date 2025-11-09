import { Bot } from 'lucide-react'

export default function TypingIndicator() {
  return (
    <div className="flex gap-4">
      <div className="flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center bg-gradient-to-br from-blue-500 to-cyan-500">
        <Bot className="w-5 h-5 text-white" />
      </div>
      <div className="inline-block bg-gray-800 rounded-2xl px-6 py-4">
        <div className="flex gap-1.5">
          <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full typing-dot"></div>
        </div>
      </div>
    </div>
  )
}
