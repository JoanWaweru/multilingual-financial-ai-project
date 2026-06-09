'use client'

import { useState, useRef, useEffect } from 'react'
import Link from 'next/link'
import { Send, Trash2, Loader2, Plus, Pin, PinOff, Trash, X } from 'lucide-react'
import MessageBubble from './MessageBubble'
import { sendMessage, clearChat, getChatHistory, getChatSessions, renameChat, pinChat, deleteChat, getMe } from '@/lib/api'

const GUEST_SESSIONS_KEY = 'kfa_guest_sessions'

// Simple UUID generator for session IDs
function generateSessionId(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0
    const v = c === 'x' ? r : (r & 0x3 | 0x8)
    return v.toString(16)
  })
}

function getGuestSessionsFromStorage(): Array<{ session_id: string; title: string }> {
  if (typeof window === 'undefined') return []
  try {
    const raw = window.localStorage.getItem(GUEST_SESSIONS_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

function saveGuestSessionsToStorage(list: Array<{ session_id: string; title: string }>) {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(GUEST_SESSIONS_KEY, JSON.stringify(list))
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  confidence?: number
  sources?: Array<{ source: string; similarity: number }>
  evidence?: Array<{ text: string; source: string; similarity: number }>
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState(() => {
    if (typeof window !== 'undefined') {
      const stored = window.localStorage.getItem('kfa_session_id')
      if (stored) return stored
      const fresh = generateSessionId()
      window.localStorage.setItem('kfa_session_id', fresh)
      return fresh
    }
    return generateSessionId()
  })
  const [sessions, setSessions] = useState<Array<{ session_id: string; title?: string; summary?: string; last_message: string; pinned?: boolean; last_updated?: string }>>([])
  const [guestSessions, setGuestSessions] = useState<Array<{ session_id: string; title: string }>>([])
  const [search, setSearch] = useState('')
  const [renamingId, setRenamingId] = useState<string | null>(null)
  const [renameValue, setRenameValue] = useState('')
  const [isGuest, setIsGuest] = useState<boolean | null>(null)
  const [showGuestSaveBanner, setShowGuestSaveBanner] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const refreshAuthState = async () => {
    if (typeof window === 'undefined') return
    const token = window.localStorage.getItem('auth_token')
    if (!token) {
      setIsGuest(true)
      return
    }
    try {
      await getMe()
      setIsGuest(false)
    } catch {
      setIsGuest(true)
      window.localStorage.removeItem('auth_token')
    }
  }

  useEffect(() => {
    refreshAuthState()
    const onFocus = () => refreshAuthState()
    const onStorage = (e: StorageEvent) => {
      if (e.key === 'auth_token') refreshAuthState()
    }
    window.addEventListener('focus', onFocus)
    window.addEventListener('storage', onStorage)
    return () => {
      window.removeEventListener('focus', onFocus)
      window.removeEventListener('storage', onStorage)
    }
  }, [])

  useEffect(() => {
    if (isGuest !== true) return
    if (typeof window !== 'undefined' && window.sessionStorage.getItem('kfa_guest_banner_dismissed')) return
    const timer = setTimeout(async () => {
      try {
        await getMe()
        setIsGuest(false)
      } catch {
        setShowGuestSaveBanner(true)
      }
    }, 90000)
    return () => clearTimeout(timer)
  }, [isGuest])

  useEffect(() => {
    if (isGuest !== true) return
    if (typeof window !== 'undefined' && window.sessionStorage.getItem('kfa_guest_banner_dismissed')) return
    if (messages.length < 2) return
    const show = async () => {
      try {
        await getMe()
        setIsGuest(false)
      } catch {
        setShowGuestSaveBanner(true)
      }
    }
    show()
  }, [isGuest, messages.length])

  useEffect(() => {
    loadHistory()
    loadSessions()
    if (typeof window !== 'undefined' && isGuest === true) {
      setGuestSessions(getGuestSessionsFromStorage())
    }
  }, [sessionId, isGuest])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const loadHistory = async () => {
    try {
      const history = await getChatHistory(sessionId)
      if (history && history.history) {
        const formattedMessages: Message[] = history.history.map((msg: any, idx: number) => ({
          id: `hist-${idx}`,
          role: msg.role,
          content: msg.message,
          timestamp: new Date(),
          confidence: msg.metadata?.confidence,
          sources: msg.metadata?.sources,
          evidence: msg.metadata?.evidence,
        }))
        setMessages(formattedMessages)
      }
    } catch (error) {
      console.error('Error loading history:', error)
    }
  }

  const loadSessions = async () => {
    // Only fetch server-side sessions when the user is logged in
    if (isGuest !== false) return
    if (typeof window !== 'undefined') {
      const token = window.localStorage.getItem('auth_token')
      if (!token) return
    }
    try {
      const data = await getChatSessions()
      setSessions(data.sessions || [])
    } catch (error) {
      // If the call fails (e.g. 401), fall back to guest behaviour
      setSessions([])
    }
  }

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await sendMessage(input.trim(), sessionId)
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
        confidence: response.confidence,
        sources: response.sources,
        evidence: response.evidence,
      }

      setMessages((prev) => [...prev, assistantMessage])
      loadSessions() // refresh so title/summary from backend appear in header
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleClear = async () => {
    if (confirm('Are you sure you want to clear the chat history?')) {
      try {
        await clearChat(sessionId, 'chat')
        setMessages([])
      } catch (error) {
        console.error('Error clearing chat:', error)
      }
    }
  }

  const handleNewChat = () => {
    if (typeof window !== 'undefined' && isGuest === true && messages.length > 0) {
      const firstUser = messages.find((m) => m.role === 'user')?.content ?? ''
      const title = firstUser ? (firstUser.slice(0, 50) + (firstUser.length > 50 ? '...' : '')) : 'Chat'
      const list = getGuestSessionsFromStorage().filter((s) => s.session_id !== sessionId)
      list.unshift({ session_id: sessionId, title })
      saveGuestSessionsToStorage(list)
      setGuestSessions(list)
    }
    setMessages([])
    const newId = generateSessionId()
    setSessionId(newId)
    if (typeof window !== 'undefined') {
      window.localStorage.setItem('kfa_session_id', newId)
    }
  }

  const sidebarSessions = isGuest
    ? guestSessions.map((s) => ({
        session_id: s.session_id,
        title: s.title,
        summary: '',
        last_message: s.title,
        pinned: false,
        last_updated: undefined,
      }))
    : sessions

  const filteredSessions = sidebarSessions.filter((s) => {
    const text = `${s.title || ''} ${s.summary || ''} ${s.last_message || ''}`.toLowerCase()
    return text.includes(search.toLowerCase())
  })

  // Current session display label (title/summary for nav and header)
  const currentSession = sidebarSessions.find((s) => s.session_id === sessionId)
  const firstUserMessage = messages.find((m) => m.role === 'user')?.content ?? ''
  const currentTitle =
    currentSession?.title ||
    currentSession?.summary ||
    (firstUserMessage ? (firstUserMessage.slice(0, 50) + (firstUserMessage.length > 50 ? '...' : '')) : 'New chat')
  const currentSummary =
    currentSession?.summary && currentSession.summary !== currentTitle
      ? currentSession.summary
      : currentSession?.last_message

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const dismissGuestBanner = () => {
    setShowGuestSaveBanner(false)
    if (typeof window !== 'undefined') window.sessionStorage.setItem('kfa_guest_banner_dismissed', '1')
  }

  const lastUserMessage = [...messages].reverse().find((m) => m.role === 'user')

  const handleEditLastUser = (content: string) => {
    setInput(content)
    inputRef.current?.focus()
  }

  return (
    <div className="flex flex-col w-full min-h-[calc(100vh-220px)] md:h-[calc(100vh-200px)] bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden">
      {/* Guest: save-your-chats notification */}
      {showGuestSaveBanner && isGuest && (
        <div className="flex items-center justify-between gap-3 px-4 py-2.5 bg-blue-50 border-b border-blue-200 text-sm text-blue-900 shrink-0">
          <p className="flex-1">
            To save your chats and access them from any device, please{' '}
            <Link href="/" className="font-medium underline hover:text-blue-700">log in or register</Link> (use the menu above).
          </p>
          <button
            onClick={dismissGuestBanner}
            className="shrink-0 p-1 rounded hover:bg-blue-100 text-blue-700"
            title="Dismiss"
            aria-label="Dismiss"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}
      <div className="flex flex-col md:flex-row flex-1 min-h-0 overflow-hidden">
      {/* Sidebar */}
      <div className="w-64 border-r border-gray-200 bg-gray-50 p-3 hidden md:block">
        <div className="flex items-center justify-between">
          <div className="font-medium text-sm">My Chats</div>
          <button
            onClick={handleNewChat}
            className="p-1 rounded hover:bg-gray-200"
            title="New chat"
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search chats..."
          className="mt-3 w-full border border-gray-300 rounded px-2 py-1 text-xs"
        />
        <div className="mt-3 space-y-2 overflow-y-auto max-h-[calc(100vh-330px)]">
          {filteredSessions.length === 0 && (
            <div className="text-xs text-gray-500">
              {isGuest ? 'Start a chat; previous chats appear here when you start a new one.' : 'No sessions yet.'}
            </div>
          )}
          {filteredSessions.map((s) => {
            const label = s.title || s.summary || s.last_message || 'New chat'
            const sublabel = s.title ? (s.summary || s.last_message) : (s.summary && s.summary !== s.last_message ? s.summary : null)
            return (
            <div
              key={s.session_id}
              className={`w-full text-left rounded px-2 py-2 border ${
                s.session_id === sessionId ? 'border-primary-600 bg-white ring-1 ring-primary-500' : 'border-gray-200 bg-white'
              }`}
            >
              <button
                onClick={() => {
                  if (s.session_id === sessionId) return
                  if (typeof window !== 'undefined' && isGuest === true && messages.length > 0) {
                    const firstUser = messages.find((m) => m.role === 'user')?.content ?? ''
                    const title = firstUser ? (firstUser.slice(0, 50) + (firstUser.length > 50 ? '...' : '')) : 'Chat'
                    const list = getGuestSessionsFromStorage().filter((x) => x.session_id !== sessionId)
                    list.unshift({ session_id: sessionId, title })
                    saveGuestSessionsToStorage(list)
                    setGuestSessions(list)
                  }
                  setSessionId(s.session_id)
                  if (typeof window !== 'undefined') {
                    window.localStorage.setItem('kfa_session_id', s.session_id)
                  }
                }}
                className="w-full text-left group"
              >
                <div className="font-medium text-sm text-gray-900 line-clamp-2" title={label}>
                  {label}
                </div>
                {sublabel && (
                  <div className="text-xs text-gray-500 mt-0.5 line-clamp-2" title={sublabel}>
                    {sublabel}
                  </div>
                )}
              </button>
              {s.last_updated && (
                <div className="text-[10px] text-gray-500 mt-1">{s.last_updated}</div>
              )}
              {!isGuest && (
              <div className="mt-2">
                {renamingId === s.session_id ? (
                  <div className="flex items-center space-x-2">
                    <input
                      type="text"
                      value={renameValue}
                      onChange={(e) => setRenameValue(e.target.value)}
                      className="border border-gray-300 rounded px-2 py-1 text-xs w-full"
                      placeholder="New title"
                    />
                    <button
                      onClick={async (e) => {
                        e.stopPropagation()
                        await renameChat(s.session_id, renameValue)
                        setRenamingId(null)
                        setRenameValue('')
                        loadSessions()
                      }}
                      className="text-xs text-primary-600"
                    >
                      Save
                    </button>
                  </div>
                ) : (
                  <div className="flex items-center space-x-2 text-[10px] text-gray-500">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        setRenamingId(s.session_id)
                        setRenameValue(s.title || s.summary || s.last_message)
                      }}
                      className="hover:text-gray-800"
                    >
                      Rename
                    </button>
                    <button
                      onClick={async (e) => {
                        e.stopPropagation()
                        await pinChat(s.session_id, !s.pinned)
                        loadSessions()
                      }}
                      className="hover:text-gray-800 flex items-center space-x-1"
                    >
                      {s.pinned ? <PinOff className="w-3 h-3" /> : <Pin className="w-3 h-3" />}
                      <span>{s.pinned ? 'Unpin' : 'Pin'}</span>
                    </button>
                    <button
                      onClick={async (e) => {
                        e.stopPropagation()
                        await deleteChat(s.session_id)
                        if (s.session_id === sessionId) {
                          handleNewChat()
                        }
                        loadSessions()
                      }}
                      className="hover:text-red-600 flex items-center space-x-1"
                    >
                      <Trash className="w-3 h-3" />
                      <span>Delete</span>
                    </button>
                  </div>
                )}
              </div>
              )}
              {isGuest && (
                <div className="mt-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      const list = getGuestSessionsFromStorage().filter((x) => x.session_id !== s.session_id)
                      saveGuestSessionsToStorage(list)
                      setGuestSessions(list)
                      if (s.session_id === sessionId) handleNewChat()
                    }}
                    className="text-[10px] text-gray-500 hover:text-red-600"
                  >
                    Remove from list
                  </button>
                </div>
              )}
            </div>
          )})}
        </div>
      </div>

      <div className="flex-1 flex flex-col min-w-0">
      {/* Chat Header: current chat title and summary */}
      <div className="flex flex-col gap-1 md:flex-row md:items-center md:justify-between p-4 border-b border-gray-200 bg-gray-50">
        <div className="min-w-0 flex-1">
          <h2 className="text-lg font-semibold text-gray-900 truncate" title={currentTitle}>
            {currentTitle}
          </h2>
          {currentSummary && (
            <p className="text-sm text-gray-600 truncate mt-0.5" title={currentSummary}>
              {currentSummary.length > 72 ? currentSummary.slice(0, 72) + '...' : currentSummary}
            </p>
          )}
        </div>
        <div className="flex items-center space-x-2 shrink-0 mt-2 md:mt-0">
            <button
              onClick={handleNewChat}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              title="New chat"
            >
              <Plus className="w-5 h-5" />
            </button>
          <button
            onClick={handleClear}
            className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            title="Clear chat"
          >
            <Trash2 className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center text-gray-500">
            <p className="text-lg mb-2">Welcome! 👋</p>
            <p className="text-sm">
              Ask me about SACCOs, banks, investments, budgeting, or any personal finance topic.
            </p>
            <p className="text-sm mt-2">
              I can respond in English or Kiswahili.
            </p>
          </div>
        )}
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            sessionId={sessionId}
            canEdit={message.role === 'user' && message.id === lastUserMessage?.id}
            onEdit={handleEditLastUser}
          />
        ))}
        {isLoading && (
          <div className="flex items-center space-x-2 text-gray-500">
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>Thinking...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Disclaimer */}
      <div className="px-4 py-2 bg-yellow-50 border-t border-yellow-200">
        <p className="text-xs text-yellow-800">
          ⚠️ This AI is not a licensed financial advisor. Please consult with qualified professionals for major financial decisions.
        </p>
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <div className="flex flex-col gap-2 md:flex-row md:items-end">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about SACCOs, investments, budgeting..."
            className="flex-1 resize-none border border-gray-300 rounded-lg px-4 py-3 bg-white text-gray-900 placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent w-full"
            rows={1}
            style={{ minHeight: '48px', maxHeight: '120px' }}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="p-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors md:self-end"
          >
            <Send className="w-5 h-5" />
          </button>
          </div>
        </div>
      </div>
      </div>
    </div>
  )
}

