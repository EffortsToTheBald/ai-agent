import { useState } from 'react'
import { MessageSquare, Plus, MoreHorizontal, Check, X, Edit3, Trash2 } from 'lucide-react'

export default function Sidebar({ sessions, current, onSelect, onCreate, onRename, onDelete }) {
  const [editing, setEditing] = useState(null)
  const [editTitle, setEditTitle] = useState('')
  const [menuOpen, setMenuOpen] = useState(null)

  const startEdit = (sid, title) => {
    setMenuOpen(null)
    setEditing(sid)
    setEditTitle(title)
  }

  const confirmEdit = () => {
    if (editing && editTitle.trim()) {
      onRename(editing, editTitle.trim())
    }
    setEditing(null)
  }

  return (
    <aside className="w-64 bg-gray-900 text-gray-200 flex flex-col shrink-0">
      <div className="p-3">
        <button onClick={onCreate}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-primary-500 to-purple-400 text-white rounded-lg font-medium text-sm hover:shadow-lg transition">
          <Plus size={16} /> 新建对话
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-2 space-y-1">
        {sessions.map(s => (
          <div key={s.id} className="group relative">
            {editing === s.id ? (
              <div className="flex items-center gap-1 p-1">
                <input value={editTitle} onChange={e => setEditTitle(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && confirmEdit()}
                  className="flex-1 px-2 py-1 text-sm bg-gray-800 border border-gray-700 rounded text-white outline-none focus:border-primary-500"
                  autoFocus />
                <button onClick={confirmEdit} className="p-1 text-green-400 hover:text-green-300"><Check size={14} /></button>
                <button onClick={() => setEditing(null)} className="p-1 text-gray-400 hover:text-gray-300"><X size={14} /></button>
              </div>
            ) : (
              <>
                <div className={`flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer text-sm transition
                  ${current === s.id ? 'bg-primary-500/20 text-white' : 'hover:bg-white/5 text-gray-300'}`}
                  onClick={() => onSelect(s.id)}>
                  <MessageSquare size={14} className="shrink-0 opacity-50" />
                  <span className="flex-1 truncate">{s.title}</span>
                  <button onClick={e => { e.stopPropagation(); setMenuOpen(menuOpen === s.id ? null : s.id) }}
                    className="p-0.5 opacity-0 group-hover:opacity-100 hover:text-white transition">
                    <MoreHorizontal size={14} />
                  </button>
                </div>
                {menuOpen === s.id && (
                  <div className="absolute right-2 top-full mt-1 z-20 bg-gray-800 border border-gray-700 rounded-lg shadow-xl py-1 w-32"
                    onClick={e => e.stopPropagation()}>
                    <button onClick={() => startEdit(s.id, s.title)}
                      className="w-full flex items-center gap-2 px-3 py-1.5 text-sm text-gray-300 hover:bg-white/10 transition">
                      <Edit3 size={13} /> 重命名
                    </button>
                    <button onClick={() => { setMenuOpen(null); onDelete(s.id) }}
                      className="w-full flex items-center gap-2 px-3 py-1.5 text-sm text-red-400 hover:bg-white/10 transition">
                      <Trash2 size={13} /> 删除
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        ))}
      </div>

      <div className="p-3 border-t border-gray-800">
        <p className="text-[10px] text-gray-500 text-center">Powered by ReAct Agent</p>
      </div>
    </aside>
  )
}