'use client'

import { useEffect, useState } from 'react'
import { getChatSessions, exportChat, getMe } from '@/lib/api'

interface SessionSummary {
  session_id: string
  last_message: string
  last_role: string
  last_updated?: string
}

export default function ProfilePage() {
  const [me, setMe] = useState<any>(null)
  const [sessions, setSessions] = useState<SessionSummary[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const load = async () => {
      try {
        const meData = await getMe()
        const sessionData = await getChatSessions()
        setMe(meData)
        setSessions(sessionData.sessions || [])
      } catch {
        setError('Please log in to view your profile and chats.')
      }
    }
    load()
  }, [])

  return (
    <div className="max-w-5xl mx-auto px-4 py-6">
      <h2 className="text-xl font-semibold text-gray-900">My Profile</h2>
      <p className="text-sm text-gray-600 mt-1">
        View your chat sessions and export history.
      </p>

      {error && <div className="mt-4 text-sm text-gray-600">{error}</div>}

      {!error && (
        <div className="mt-6 space-y-6">
          <div className="rounded border border-gray-200 p-4">
            <div className="text-sm text-gray-600">Email</div>
            <div className="font-medium">{me?.email}</div>
            {me?.full_name && (
              <>
                <div className="text-sm text-gray-600 mt-2">Name</div>
                <div className="font-medium">{me.full_name}</div>
              </>
            )}
          </div>

          <div className="rounded border border-gray-200 p-4">
            <div className="font-medium">My Chats</div>
            <div className="mt-3 space-y-3">
              {sessions.length === 0 && (
                <div className="text-sm text-gray-600">No sessions found.</div>
              )}
              {sessions.map((session) => (
                <div key={session.session_id} className="border border-gray-200 rounded p-3">
                  <div className="text-sm text-gray-700">
                    Session: {session.session_id}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    Last updated: {session.last_updated}
                  </div>
                  <div className="text-sm text-gray-600 mt-2">
                    {session.last_role}: {session.last_message}
                  </div>
                  <div className="mt-3 flex items-center space-x-2">
                    <ExportButton sessionId={session.session_id} format="csv" />
                    <ExportButton sessionId={session.session_id} format="pdf" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function ExportButton({ sessionId, format }: { sessionId: string; format: 'csv' | 'pdf' }) {
  const label = format.toUpperCase()
  return (
    <button
      onClick={async () => {
        const blob = await exportChat(sessionId, format)
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `chat_${sessionId}.${format}`
        a.click()
        window.URL.revokeObjectURL(url)
      }}
      className="px-3 py-1 text-xs rounded border border-gray-300 hover:bg-gray-50"
    >
      Export {label}
    </button>
  )
}
