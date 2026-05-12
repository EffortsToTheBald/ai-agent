import { useState } from 'react'
import { auth } from '../api/client'

export default function Login({ onLogin }) {
  const [isRegister, setIsRegister] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [password2, setPassword2] = useState('')
  const [role, setRole] = useState('user')
  const [adminCode, setAdminCode] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (!username.trim() || !password) { setError('请输入用户名和密码'); return }
    if (isRegister) {
      if (password.length < 6) { setError('密码长度至少6位'); return }
      if (password !== password2) { setError('两次密码不一致'); return }
    }
    setLoading(true)
    try {
      const user = isRegister
        ? await auth.register({ username: username.trim(), password, role, admin_code: adminCode })
        : await auth.login({ username: username.trim(), password })
      onLogin(user)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-purple-50">
      <div className="w-full max-w-md p-8 bg-white rounded-2xl shadow-lg">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-purple-400 rounded-2xl flex items-center justify-center text-3xl mx-auto mb-4 shadow-lg">🤖</div>
          <h1 className="text-2xl font-bold text-gray-800">智能客服系统</h1>
          <p className="text-gray-400 text-sm mt-1">{isRegister ? '创建新账号' : '登录到您的账号'}</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">用户名</label>
            <input type="text" value={username} onChange={e => setUsername(e.target.value)}
              placeholder="请输入用户名"
              className="w-full px-4 py-2.5 rounded-lg border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">密码</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)}
              placeholder="请输入密码"
              className="w-full px-4 py-2.5 rounded-lg border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition" />
          </div>

          {isRegister && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">确认密码</label>
                <input type="password" value={password2} onChange={e => setPassword2(e.target.value)}
                  placeholder="再次输入密码"
                  className="w-full px-4 py-2.5 rounded-lg border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-600 mb-1">注册身份</label>
                <div className="flex gap-4">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="radio" name="role" value="user" checked={role === 'user'} onChange={() => setRole('user')}
                      className="text-primary-500 focus:ring-primary-500" />
                    <span className="text-sm text-gray-700">普通用户</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input type="radio" name="role" value="admin" checked={role === 'admin'} onChange={() => setRole('admin')}
                      className="text-primary-500 focus:ring-primary-500" />
                    <span className="text-sm text-gray-700">管理员</span>
                  </label>
                </div>
              </div>
              {role === 'admin' && (
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">管理员验证码</label>
                  <input type="password" value={adminCode} onChange={e => setAdminCode(e.target.value)}
                    placeholder="请输入验证码"
                    className="w-full px-4 py-2.5 rounded-lg border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-100 outline-none transition" />
                </div>
              )}
            </>
          )}

          {error && <p className="text-red-500 text-sm">{error}</p>}

          <button type="submit" disabled={loading}
            className="w-full py-2.5 bg-gradient-to-r from-primary-500 to-purple-400 text-white rounded-lg font-semibold hover:shadow-lg hover:from-primary-600 hover:to-purple-500 transition disabled:opacity-50">
            {loading ? '处理中...' : (isRegister ? '注 册' : '登 录')}
          </button>
        </form>

        <p className="text-center text-sm text-gray-400 mt-6">
          {isRegister ? '已有账号？' : '还没有账号？'}
          <button onClick={() => { setIsRegister(!isRegister); setError('') }}
            className="text-primary-500 hover:text-primary-600 font-medium ml-1">
            {isRegister ? '去登录' : '去注册'}
          </button>
        </p>
      </div>
    </div>
  )
}
