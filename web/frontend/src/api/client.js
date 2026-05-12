const BASE = '/api'

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || '请求失败')
  }
  return res.json()
}

// Auth
export const auth = {
  register: (data) => request('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  login: (data) => request('/auth/login', { method: 'POST', body: JSON.stringify(data) }),
  listUsers: () => request('/auth/users'),
  updateRole: (id, role) => request(`/auth/users/${id}/role?role=${role}`, { method: 'PUT' }),
  deleteUser: (id) => request(`/auth/users/${id}`, { method: 'DELETE' }),
}

// Sessions
export const sessions = {
  list: (userId) => request(`/chat/sessions?user_id=${userId}`),
  create: (userId, data) => request(`/chat/sessions?user_id=${userId}`, { method: 'POST', body: JSON.stringify(data) }),
  rename: (id, title) => request(`/chat/sessions/${id}/rename`, { method: 'PUT', body: JSON.stringify({ title }) }),
  delete: (id) => request(`/chat/sessions/${id}`, { method: 'DELETE' }),
  getMessages: (id) => request(`/chat/sessions/${id}/messages`),
  addMessage: (id, userId, data) => request(`/chat/sessions/${id}/messages?user_id=${userId}`, { method: 'POST', body: JSON.stringify(data) }),
}

// Chat streaming
export async function* chatStream(sessionId, message) {
  const res = await fetch(`${BASE}/chat/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || '流请求失败')
  }
  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop()
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6))
          yield data
        } catch {}
      }
    }
  }
}

// Admin
export const admin = {
  listDomains: () => request('/admin/domains'),
  createDomain: (data) => request('/admin/domains', { method: 'POST', body: JSON.stringify(data) }),
  deleteDomain: (id) => request(`/admin/domains/${id}`, { method: 'DELETE' }),
  listEntries: (domainId) => request(`/admin/domains/${domainId}/entries`),
  addEntry: (domainId, data) => request(`/admin/domains/${domainId}/entries`, { method: 'POST', body: JSON.stringify(data) }),
  updateEntry: (id, data) => request(`/admin/entries/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteEntry: (id) => request(`/admin/entries/${id}`, { method: 'DELETE' }),
  listFiles: (domainId) => request(`/admin/domains/${domainId}/files`),
  deleteFile: (id) => request(`/admin/files/${id}`, { method: 'DELETE' }),
  uploadFile: async (domainId, file) => {
    const form = new FormData()
    form.append('file', file)
    const res = await fetch(`${BASE}/admin/domains/${domainId}/files/upload`, { method: 'POST', body: form })
    if (!res.ok) throw new Error('上传失败')
    return res.json()
  },
  reindex: (domainId) => request(`/admin/domains/${domainId}/reindex`, { method: 'POST' }),
  watcher: {
    status: () => request('/admin/system/watcher'),
    start: () => request('/admin/system/watcher/start', { method: 'POST' }),
    stop: () => request('/admin/system/watcher/stop', { method: 'POST' }),
  },
}
