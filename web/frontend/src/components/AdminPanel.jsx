import { useState, useEffect } from 'react'
import { admin, auth } from '../api/client'
import { Users, Globe, BookOpen, FileText, Settings, Trash2, Upload, RefreshCw, Play, Square } from 'lucide-react'

export default function AdminPanel({ user }) {
  const [tab, setTab] = useState('users')

  const tabs = [
    { key: 'users', label: '用户管理', icon: Users },
    { key: 'domains', label: '领域管理', icon: Globe },
    { key: 'kb', label: '知识库管理', icon: BookOpen },
    { key: 'entries', label: '知识条目', icon: FileText },
    { key: 'system', label: '系统状态', icon: Settings },
  ]

  return (
    <div className="h-full flex bg-gray-50">
      <aside className="w-48 bg-white border-r border-gray-100 p-3 space-y-1 shrink-0">
        <h3 className="text-xs font-semibold text-gray-400 uppercase px-3 mb-2">管理后台</h3>
        {tabs.map(t => (
          <button key={t.key} onClick={() => setTab(t.key)}
            className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition
              ${tab === t.key ? 'bg-primary-50 text-primary-600 font-medium' : 'text-gray-500 hover:bg-gray-50'}`}>
            <t.icon size={16} /> {t.label}
          </button>
        ))}
      </aside>
      <main className="flex-1 overflow-y-auto p-6">
        {tab === 'users' && <UsersPanel currentUser={user} />}
        {tab === 'domains' && <DomainsPanel />}
        {tab === 'kb' && <KBPanel />}
        {tab === 'entries' && <EntriesPanel />}
        {tab === 'system' && <SystemPanel />}
      </main>
    </div>
  )
}

function UsersPanel({ currentUser }) {
  const [users, setUsers] = useState([])
  useEffect(() => { auth.listUsers().then(setUsers) }, [])

  const updateRole = async (id, role) => {
    await auth.updateRole(id, role)
    setUsers(prev => prev.map(u => u.id === id ? { ...u, role } : u))
  }

  const deleteUser = async (id) => {
    await auth.deleteUser(id)
    setUsers(prev => prev.filter(u => u.id !== id))
  }

  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold text-gray-800">用户管理</h2>
      {users.map(u => (
        <div key={u.id} className="flex items-center gap-4 p-3 bg-white rounded-lg border border-gray-100">
          <div className="w-8 h-8 bg-gradient-to-br from-primary-400 to-purple-300 rounded-full flex items-center justify-center text-white text-sm font-semibold">
            {u.username[0].toUpperCase()}
          </div>
          <span className="font-medium text-gray-700 flex-1">{u.username}
            {u.id === currentUser?.id && <span className="text-xs text-gray-400 ml-2">(当前用户)</span>}
          </span>
          <select value={u.role} onChange={e => updateRole(u.id, e.target.value)}
            className="text-sm border border-gray-200 rounded-lg px-2 py-1 outline-none focus:border-primary-500">
            <option value="user">普通用户</option>
            <option value="admin">管理员</option>
          </select>
          <span className={`text-xs px-2 py-0.5 rounded-full ${u.role === 'admin' ? 'bg-red-50 text-red-500' : 'bg-teal-50 text-teal-600'}`}>
            {u.role === 'admin' ? '管理员' : '普通用户'}
          </span>
          {u.id !== currentUser?.id && (
            <button onClick={() => deleteUser(u.id)} className="text-gray-400 hover:text-red-500 transition"><Trash2 size={16} /></button>
          )}
        </div>
      ))}
    </div>
  )
}

function DomainsPanel() {
  const [domains, setDomains] = useState([])
  const [name, setName] = useState('')
  const [desc, setDesc] = useState('')
  const [prompt, setPrompt] = useState('')
  useEffect(() => { admin.listDomains().then(setDomains) }, [])

  const create = async () => {
    if (!name.trim()) return
    try {
      const d = await admin.createDomain({ name: name.trim(), description: desc, prompt_template: prompt })
      setDomains(prev => [...prev, d])
      setName(''); setDesc(''); setPrompt('')
    } catch {}
  }

  const remove = async (id) => {
    await admin.deleteDomain(id)
    setDomains(prev => prev.filter(d => d.id !== id))
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-800">领域管理</h2>
      <div className="space-y-2">
        {domains.map(d => (
          <div key={d.id} className="flex items-center gap-3 p-3 bg-white rounded-lg border border-gray-100">
            <Globe size={16} className="text-primary-400" />
            <span className="font-medium text-gray-700">{d.name}</span>
            <span className="text-sm text-gray-400">{d.description || '无描述'}</span>
            {d.id !== 'default' && (
              <button onClick={() => remove(d.id)} className="ml-auto text-gray-400 hover:text-red-500"><Trash2 size={16} /></button>
            )}
          </div>
        ))}
      </div>
      <div className="bg-white p-4 rounded-lg border border-gray-100 space-y-3">
        <h3 className="text-sm font-medium text-gray-600">创建新领域</h3>
        <input value={name} onChange={e => setName(e.target.value)} placeholder="领域名称" className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm outline-none focus:border-primary-500" />
        <input value={desc} onChange={e => setDesc(e.target.value)} placeholder="领域描述" className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm outline-none focus:border-primary-500" />
        <textarea value={prompt} onChange={e => setPrompt(e.target.value)} placeholder="Prompt 模板（可选）" rows={3} className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm outline-none focus:border-primary-500 resize-none" />
        <button onClick={create} className="px-4 py-2 bg-gradient-to-r from-primary-500 to-purple-400 text-white rounded-lg text-sm font-medium hover:shadow-lg transition">创建领域</button>
      </div>
    </div>
  )
}

function KBPanel() {
  const [domains, setDomains] = useState([])
  const [selected, setSelected] = useState(null)
  const [selectedDomain, setSelectedDomain] = useState(null)
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [msg, setMsg] = useState(null)

  useEffect(() => { admin.listDomains().then(d => { setDomains(d); if (d.length) { setSelected(d[0].id); setSelectedDomain(d[0]) } }) }, [])
  useEffect(() => { if (selected) { admin.listFiles(selected).then(setFiles); setSelectedDomain(domains.find(d => d.id === selected)) } }, [selected])

  const handleUpload = async (e) => {
    const fileList = e.target.files
    if (!fileList.length) return
    setUploading(true)
    let ok = 0, fail = 0
    for (const f of fileList) {
      try { await admin.uploadFile(selected, f); ok++ } catch { fail++ }
    }
    setUploading(false)
    setMsg({ type: ok ? 'success' : 'error', text: ok ? `成功上传 ${ok} 个文件` : `${fail} 个文件上传失败` })
    admin.listFiles(selected).then(setFiles)
    setTimeout(() => setMsg(null), 3000)
  }

  const handleReindex = async () => {
    try {
      const res = await admin.reindex(selected)
      setMsg({ type: 'success', text: `索引完成，新增 ${res.indexed} 个文件` })
    } catch { setMsg({ type: 'error', text: '索引失败' }) }
    setTimeout(() => setMsg(null), 3000)
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-800">知识库管理</h2>
      <select value={selected || ''} onChange={e => setSelected(e.target.value)}
        className="px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:border-primary-500">
        {domains.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
      </select>

      {selectedDomain?.collection_name && (
        <p className="text-xs text-gray-400">向量集合: <code className="bg-gray-100 px-1.5 py-0.5 rounded text-gray-600">{selectedDomain.collection_name}</code></p>
      )}

      <div className="flex gap-2">
        <button onClick={handleReindex}
          className="flex items-center gap-1 px-3 py-2 bg-gradient-to-r from-primary-500 to-purple-400 text-white rounded-lg text-sm font-medium hover:shadow-lg transition">
          <RefreshCw size={14} /> 索引文件
        </button>
        <label className="flex items-center gap-1 px-3 py-2 bg-white border border-gray-200 rounded-lg text-sm text-gray-600 cursor-pointer hover:border-primary-300 transition">
          <Upload size={14} /> 上传文件
          <input type="file" multiple accept=".pdf,.txt,.md" onChange={handleUpload} className="hidden" />
        </label>
      </div>

      {msg && <div className={`text-sm px-3 py-2 rounded-lg ${msg.type === 'success' ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-500'}`}>{msg.text}</div>}

      <div className="space-y-1">
        {files.map((f, i) => (
          <div key={f.id || `disk-${i}`} className="flex items-center gap-2 px-3 py-2 bg-white rounded-lg border border-gray-100 text-sm">
            <span>{f.filename.endsWith('.pdf') ? '📕' : f.filename.endsWith('.md') ? '📝' : '📄'}</span>
            <span className="flex-1 text-gray-700">{f.filename}</span>
            <span className={`text-xs ${
              f.status === 'indexed' ? 'text-green-500' :
              f.status === 'disk_only' ? 'text-blue-400' :
              'text-yellow-500'
            }`}>
              {f.status === 'indexed' ? '✅ 已索引' :
               f.status === 'disk_only' ? '💾 仅磁盘' :
               '⏳ 待索引'}
            </span>
            {f.id && (
              <button onClick={() => admin.deleteFile(f.id).then(() => setFiles(prev => prev.filter(x => x.id !== f.id)))}
                className="text-gray-400 hover:text-red-500"><Trash2 size={14} /></button>
            )}
          </div>
        ))}
        {files.length === 0 && <p className="text-sm text-gray-400">暂无文件</p>}
      </div>
    </div>
  )
}

function EntriesPanel() {
  const [domains, setDomains] = useState([])
  const [selected, setSelected] = useState(null)
  const [entries, setEntries] = useState([])
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')

  useEffect(() => { admin.listDomains().then(d => { setDomains(d); if (d.length) setSelected(d[0].id) }) }, [])
  useEffect(() => { if (selected) admin.listEntries(selected).then(setEntries) }, [selected])

  const addEntry = async () => {
    if (!title.trim() || !content.trim()) return
    const e = await admin.addEntry(selected, { title: title.trim(), content: content.trim() })
    setEntries(prev => [{ ...e, content }, ...prev])
    setTitle(''); setContent('')
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-800">知识条目管理</h2>
      <select value={selected || ''} onChange={e => setSelected(e.target.value)}
        className="px-3 py-2 border border-gray-200 rounded-lg text-sm outline-none focus:border-primary-500">
        {domains.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
      </select>

      <div className="space-y-2">
        {entries.map(e => (
          <div key={e.id} className="p-3 bg-white rounded-lg border border-gray-100">
            <div className="flex items-center justify-between">
              <span className="font-medium text-gray-700">{e.title}</span>
              <button onClick={() => admin.deleteEntry(e.id).then(() => setEntries(prev => prev.filter(x => x.id !== e.id)))}
                className="text-gray-400 hover:text-red-500"><Trash2 size={14} /></button>
            </div>
            <p className="text-sm text-gray-400 mt-1">{e.content?.slice(0, 80)}...</p>
          </div>
        ))}
      </div>

      <div className="bg-white p-4 rounded-lg border border-gray-100 space-y-3">
        <h3 className="text-sm font-medium text-gray-600">添加知识条目</h3>
        <input value={title} onChange={e => setTitle(e.target.value)} placeholder="条目标题" className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm outline-none focus:border-primary-500" />
        <textarea value={content} onChange={e => setContent(e.target.value)} placeholder="详细的知识内容..." rows={4} className="w-full px-3 py-2 rounded-lg border border-gray-200 text-sm outline-none focus:border-primary-500 resize-none" />
        <button onClick={addEntry} className="px-4 py-2 bg-gradient-to-r from-primary-500 to-purple-400 text-white rounded-lg text-sm font-medium hover:shadow-lg transition">添加条目</button>
      </div>
    </div>
  )
}

function SystemPanel() {
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)
  const [msg, setMsg] = useState(null)

  const loadStatus = async () => {
    try {
      const s = await admin.watcher.status()
      setStatus(s)
    } catch {}
  }

  useEffect(() => { loadStatus() }, [])

  const handleStart = async () => {
    setLoading(true)
    try {
      const res = await admin.watcher.start()
      setMsg({ type: 'success', text: res.message })
      loadStatus()
    } catch (err) {
      setMsg({ type: 'error', text: err.message })
    }
    setLoading(false)
    setTimeout(() => setMsg(null), 3000)
  }

  const handleStop = async () => {
    setLoading(true)
    try {
      const res = await admin.watcher.stop()
      setMsg({ type: 'success', text: res.message })
      loadStatus()
    } catch (err) {
      setMsg({ type: 'error', text: err.message })
    }
    setLoading(false)
    setTimeout(() => setMsg(null), 3000)
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-800">系统状态</h2>
      {status && (
        <div className="bg-white p-4 rounded-lg border border-gray-100 space-y-4">
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-500">文件监听:</span>
            {status.available ? (
              <span className={`flex items-center gap-1.5 text-sm font-medium ${status.running ? 'text-green-500' : 'text-gray-400'}`}>
                <span className={`w-2 h-2 rounded-full ${status.running ? 'bg-green-500' : 'bg-gray-400'}`} />
                {status.running ? '运行中' : '未启动'}
              </span>
            ) : (
              <span className="text-sm text-red-500">watchdog 未安装</span>
            )}
          </div>
          {status.available && (
            <div className="flex gap-2">
              {!status.running ? (
                <button onClick={handleStart} disabled={loading}
                  className="flex items-center gap-1 px-3 py-2 bg-gradient-to-r from-primary-500 to-purple-400 text-white rounded-lg text-sm font-medium hover:shadow-lg transition disabled:opacity-50">
                  <Play size={14} /> 启动文件监听
                </button>
              ) : (
                <button onClick={handleStop} disabled={loading}
                  className="flex items-center gap-1 px-3 py-2 bg-red-500 text-white rounded-lg text-sm font-medium hover:bg-red-600 transition disabled:opacity-50">
                  <Square size={14} /> 停止文件监听
                </button>
              )}
            </div>
          )}
        </div>
      )}
      {msg && <div className={`text-sm px-3 py-2 rounded-lg ${msg.type === 'success' ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-500'}`}>{msg.text}</div>}
    </div>
  )
}
