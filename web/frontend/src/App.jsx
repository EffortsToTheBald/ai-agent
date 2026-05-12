import { useState, useEffect } from 'react'
import Login from './pages/Login'
import Chat from './pages/Chat'

export default function App() {
  const [user, setUser] = useState(null)

  useEffect(() => {
    const saved = localStorage.getItem('user')
    if (saved) setUser(JSON.parse(saved))
  }, [])

  const handleLogin = (u) => {
    setUser(u)
    localStorage.setItem('user', JSON.stringify(u))
  }

  const handleLogout = () => {
    setUser(null)
    localStorage.removeItem('user')
  }

  if (!user) return <Login onLogin={handleLogin} />
  return <Chat user={user} onLogout={handleLogout} />
}
