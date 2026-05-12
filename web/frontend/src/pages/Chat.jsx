import { useState, useEffect } from 'react'
import { sessions, chatStream, admin } from '../api/client'
import Sidebar from '../components/Sidebar'
import ChatArea from '../components/ChatArea'
import AdminPanel from '../components/AdminPanel'

export default function Chat({ user, onLogout }) {
  const [sessionList, setSessionList] = useState([])
  const [currentSession, setCurrentSession] = useState(null)
  const [messages, setMessages] = useState([])
  const [showAdmin, setShowAdmin] = useState(false)

  useEffect(() => {
    (async () => {
      try {
        const list = await sessions.list(user.id)
        setSessionList(list)
        if (list.length > 0) selectSession(list[0].id)
      } catch {}
    })()
  }, [])

  const refreshSessionList = async () => {
    try {
      const list = await sessions.list(user.id)
      setSessionList(list)
    } catch {}
  }

  const selectSession = async (sid) => {
    setCurrentSession(sid)
    try {
      const msgs = await sessions.getMessages(sid)
      setMessages(msgs)
    } catch { setMessages([]) }
  }

  const createSession = async () => {
    try {
      const s = await sessions.create(user.id, { title: '新对话', domain: 'default' })
      setSessionList(prev => [s, ...prev])
      setCurrentSession(s.id)
      setMessages([])
    } catch {}
  }

  const renameSession = async (sid, title) => {
    await sessions.rename(sid, title)
    setSessionList(prev => prev.map(s => s.id === sid ? { ...s, title } : s))
  }

  const deleteSession = async (sid) => {
    await sessions.delete(sid)
    const newList = sessionList.filter(s => s.id !== sid)
    setSessionList(newList)
    if (currentSession === sid) {
      if (newList.length > 0) { selectSession(newList[0].id) }
      else { setCurrentSession(null); setMessages([]) }
    }
  }

  const sendMessage = async (content) => {
    let sid = currentSession

    // Create session if needed
    if (!sid) {
      const s = await sessions.create(user.id, { title: content.slice(0, 20) + '...', domain: 'default' })
      sid = s.id
      setSessionList(prev => [s, ...prev])
      setCurrentSession(sid)
    }

    // Add user message
    setMessages(prev => [...prev, { role: 'user', content }])

    // Add placeholder for assistant
    setMessages(prev => [...prev, { role: 'assistant', content: '' }])

    let fullResponse = ''
    try {
      for await (const data of chatStream(sid, content)) {
        if (data.error) {
          throw new Error(data.error)
        }
        if (data.token) {
          fullResponse += data.token
          setMessages(prev => {
            const updated = [...prev]
            updated[updated.length - 1] = { role: 'assistant', content: fullResponse }
            return updated
          })
        }
      }
    } catch (err) {
      setMessages(prev => {
        const updated = [...prev]
        updated[updated.length - 1] = { role: 'assistant', content: `错误: ${err.message}` }
        return updated
      })
    }

    // Refresh session list
    refreshSessionList()
  }

  return (
    <div className="h-screen flex flex-col">
      <header className="h-14 bg-white border-b border-gray-100 flex items-center px-6 shrink-0 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-purple-400 rounded-lg flex items-center justify-center text-white text-sm">🤖</div>
          <span className="font-semibold text-gray-800">智能客服</span>
          <span className="text-xs text-green-500 bg-green-50 px-2 py-0.5 rounded-full">● 在线</span>
        </div>
        <div className="ml-auto flex items-center gap-3">
          <span className="text-sm text-gray-500">{user.username}</span>
          <span className={`text-xs px-2 py-0.5 rounded-full ${user.role === 'admin' ? 'bg-red-50 text-red-500' : 'bg-teal-50 text-teal-600'}`}>
            {user.role === 'admin' ? '管理员' : '普通用户'}
          </span>
          {user.role === 'admin' && (
            <button onClick={() => setShowAdmin(!showAdmin)}
              className="text-xs px-3 py-1 rounded-lg bg-primary-50 text-primary-600 hover:bg-primary-100 transition">
              {showAdmin ? '返回聊天' : '管理后台'}
            </button>
          )}
          <button onClick={onLogout} className="text-xs px-3 py-1 rounded-lg bg-gray-100 text-gray-500 hover:bg-gray-200 transition">退出</button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          sessions={sessionList}
          current={currentSession}
          onSelect={selectSession}
          onCreate={createSession}
          onRename={renameSession}
          onDelete={deleteSession}
        />
        <main className="flex-1 overflow-hidden">
          {showAdmin ? <AdminPanel user={user} /> : <ChatArea messages={messages} onSend={sendMessage} />}
        </main>
      </div>
    </div>
  )
}
