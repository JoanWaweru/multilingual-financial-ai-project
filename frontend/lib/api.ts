import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers = config.headers || {}
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

export interface ChatResponse {
  response: string
  confidence: number
  session_id: string
  user_id: string
  retrieved_documents: number
  sources: Array<{ source: string; similarity: number }>
  evidence?: Array<{ text: string; source: string; similarity: number }>
  disclaimer?: string
}

export async function sendMessage(message: string, sessionId: string): Promise<ChatResponse> {
  const response = await api.post<ChatResponse>('/api/chat/', {
    message,
    session_id: sessionId,
  })
  return response.data
}

export async function getChatHistory(sessionId: string) {
  const response = await api.get(`/api/chat/history/${sessionId}`)
  return response.data
}

export async function getChatSessions() {
  const response = await api.get('/api/chat/sessions')
  return response.data
}

export async function exportChat(sessionId: string, format: 'csv' | 'pdf') {
  const response = await api.get(`/api/chat/export/${sessionId}`, {
    params: { format },
    responseType: 'blob',
  })
  return response.data
}

export async function clearChat(sessionId: string, clearType: 'chat' | 'preferences' | 'all' = 'chat') {
  const response = await api.post('/api/memory/clear', {
    session_id: sessionId,
    clear_type: clearType,
  })
  return response.data
}

export async function savePreference(sessionId: string, key: string, value: any) {
  const response = await api.post('/api/memory/preferences', {
    session_id: sessionId,
    key,
    value,
  })
  return response.data
}

export async function getPreferences(sessionId: string) {
  const response = await api.get(`/api/memory/preferences/${sessionId}`)
  return response.data
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user_id: string
  email: string
  full_name?: string
  role: string
}

export async function registerUser(email: string, password: string, fullName?: string) {
  const response = await api.post<AuthResponse>('/api/auth/register', {
    email,
    password,
    full_name: fullName,
  })
  return response.data
}

export async function loginUser(email: string, password: string) {
  const response = await api.post<AuthResponse>('/api/auth/login', {
    email,
    password,
  })
  return response.data
}

export async function getMe() {
  const response = await api.get('/api/auth/me')
  return response.data
}

export async function uploadDocument(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post('/api/documents/ingest', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export async function getAdminOverview() {
  const response = await api.get('/api/admin/overview')
  return response.data
}

export async function getAdminFeedback() {
  const response = await api.get('/api/admin/feedback')
  return response.data
}

export async function getAdminUsers() {
  const response = await api.get('/api/admin/users')
  return response.data
}

export async function updateUserRole(userId: string, role: 'user' | 'admin' | 'moderator') {
  const response = await api.post(`/api/admin/users/${userId}/role`, null, {
    params: { role },
  })
  return response.data
}

export async function getEvalMetrics() {
  const response = await api.get('/api/eval/code-switch')
  return response.data
}

export async function submitFeedback(sessionId: string, rating: number, comment?: string, messageId?: number) {
  const response = await api.post('/api/feedback', {
    session_id: sessionId,
    message_id: messageId,
    rating,
    comment,
  })
  return response.data
}
