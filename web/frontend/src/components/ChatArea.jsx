import { useState, useRef, useEffect } from 'react'
import { Send } from 'lucide-react'

export default function ChatArea({ messages, onSend }) {
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleQuickSend = async (q) => {
    if (sending) return
    setSending(true)
    try { await onSend(q) } finally { setSending(false) }
  }

  const handleSend = async () => {
    const text = input.trim()
    if (!text || sending) return
    setInput('')
    setSending(true)
    try { await onSend(text) } finally { setSending(false) }
  }

  const quickQuestions = [
    { icon: '🔧', label: '故障排查', q: '扫地机器人无法开机怎么办？' },
    { icon: '🛒', label: '选购建议', q: '推荐一款性价比高的扫地机器人' },
    { icon: '🧹', label: '清洁保养', q: '扫地机器人如何清洁保养？' },
    { icon: '📋', label: '常见问题', q: '扫地机器人常见故障有哪些？' },
  ]

  return (
    <div className="flex flex-col h-full bg-gray-50">
      {messages.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center px-8">
          <div className="w-20 h-20 bg-gradient-to-br from-primary-500 to-purple-400 rounded-2xl flex items-center justify-center text-4xl mb-6 shadow-lg">🤖</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">你好，我是智能客服助手</h2>
          <p className="text-gray-400 mb-10">有任何问题都可以向我提问，我会尽力为您解答</p>
          <div className="grid grid-cols-2 gap-3 max-w-lg w-full">
            {quickQuestions.map(q => (
              <button key={q.label} onClick={() => handleQuickSend(q.q)}
                disabled={sending}
                className="p-4 bg-white rounded-xl border border-gray-100 text-left hover:border-primary-300 hover:shadow-md transition disabled:opacity-50">
                <span className="text-lg">{q.icon}</span>
                <p className="text-sm text-gray-600 mt-1">{q.q}</p>
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fadeInUp`}>
              <div className={`max-w-[70%] rounded-2xl px-4 py-3 text-sm leading-relaxed
                ${msg.role === 'user'
                  ? 'bg-gradient-to-r from-primary-500 to-purple-400 text-white'
                  : 'bg-white border border-gray-100 text-gray-700 shadow-sm'}`}>
                {msg.content ? msg.content : (msg.role === 'assistant' ? (
                  <span className="inline-flex items-center gap-0.5">
                    <span className="thinking-dot" />
                    <span className="thinking-dot" />
                    <span className="thinking-dot" />
                  </span>
                ) : '')}
              </div>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>
      )}

      <div className="border-t border-gray-100 bg-white p-4">
        <div className="flex items-center gap-3 max-w-3xl mx-auto">
          <input value={input} onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleSend()}
            placeholder="输入你的问题..."
            className="flex-1 px-4 py-2.5 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition text-sm"
            disabled={sending} />
          <button onClick={handleSend} disabled={sending || !input.trim()}
            className="w-10 h-10 bg-gradient-to-r from-primary-500 to-purple-400 text-white rounded-xl flex items-center justify-center hover:shadow-lg transition disabled:opacity-40">
            <Send size={18} />
          </button>
        </div>
      </div>
    </div>
  )
}
