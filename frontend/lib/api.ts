import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface ChatResponse {
  response: string
  confidence: number
  session_id: string
  user_id: string
  retrieved_documents: number
  sources: Array<{ source: string; similarity: number }>
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

