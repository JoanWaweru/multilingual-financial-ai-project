'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Trash2, Loader2, Plus, Pin, PinOff, Trash } from 'lucide-react'
import MessageBubble from './MessageBubble'
import { sendMessage, clearChat, getChatHistory, getChatSessions, renameChat, pinChat, deleteChat } from '@/lib/api'

// Simple UUID generator for session IDs
function generateSessionId(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0
    const v = c === 'x' ? r : (r & 0x3 | 0x8)
    return v.toString(16)
  })
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
  const [sessionId, setSessionId] = useState(() => generateSessionId())
  const [sessions, setSessions] = useState<Array<{ session_id: string; title?: string; summary?: string; last_message: string; pinned?: boolean; last_updated?: string }>>([])
  const [search, setSearch] = useState('')
  const [renamingId, setRenamingId] = useState<string | null>(null)
  const [renameValue, setRenameValue] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    loadHistory()
    loadSessions()
  }, [sessionId])

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
    try {
      const data = await getChatSessions()
      setSessions(data.sessions || [])
    } catch (error) {
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
    setMessages([])
    setSessionId(generateSessionId())
  }

  const filteredSessions = sessions.filter((s) => {
    const text = `${s.title || ''} ${s.last_message || ''}`.toLowerCase()
    return text.includes(search.toLowerCase())
  })

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex h-[calc(100vh-200px)] bg-white rounded-lg shadow-lg border border-gray-200">
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
          {sessions.length === 0 && (
            <div className="text-xs text-gray-500">No sessions yet.</div>
          )}
          {filteredSessions.map((s) => (
            <div
              key={s.session_id}
              className={`w-full text-left text-xs rounded px-2 py-2 border ${
                s.session_id === sessionId ? 'border-primary-600 bg-white' : 'border-gray-200 bg-white'
              }`}
            >
              <button
                onClick={() => setSessionId(s.session_id)}
                className="w-full text-left"
              >
                <div className="font-medium truncate">{s.title || s.summary || s.last_message}</div>
              </button>
              {s.last_updated && (
                <div className="text-[10px] text-gray-500 mt-1">{s.last_updated}</div>
              )}
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
            </div>
          ))}
        </div>
      </div>

      <div className="flex-1 flex flex-col">
      {/* Chat Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50">
        <h2 className="text-lg font-semibold text-gray-900">Chat</h2>
        <div className="flex items-center space-x-2">
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
          <MessageBubble key={message.id} message={message} sessionId={sessionId} />
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
        <div className="flex items-end space-x-2">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about SACCOs, investments, budgeting..."
              className="flex-1 resize-none border border-gray-300 rounded-lg px-4 py-3 bg-white text-gray-900 placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            rows={1}
            style={{ minHeight: '48px', maxHeight: '120px' }}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="p-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
          </div>
        </div>
      </div>
    </div>
  )
}

