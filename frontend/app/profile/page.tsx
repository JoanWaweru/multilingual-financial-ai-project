'use client'

import { useEffect, useState } from 'react'
import Header from '@/components/Header'
import {
  getChatSessions,
  exportChat,
  getMe,
  renameChat,
  getPreferences,
  savePreference,
} from '@/lib/api'

interface SessionSummary {
  session_id: string
  title?: string
  summary?: string
  last_message: string
  last_role: string
  last_updated?: string
}

type UserPreferences = {
  goals?: string | string[]
  risk_level?: string
  language?: string
  time_horizon?: string
}

function formatPreferenceValue(value: unknown): string {
  if (value == null || value === '') return 'Not set'
  if (Array.isArray(value)) return value.join(', ')
  return String(value)
}

function getSessionId(): string {
  if (typeof window === 'undefined') return 'profile'
  return localStorage.getItem('kfa_session_id') || 'profile'
}

export default function ProfilePage() {
  const [me, setMe] = useState<any>(null)
  const [sessions, setSessions] = useState<SessionSummary[]>([])
  const [preferences, setPreferences] = useState<UserPreferences>({})
  const [goals, setGoals] = useState('')
  const [riskLevel, setRiskLevel] = useState('')
  const [language, setLanguage] = useState('')
  const [timeHorizon, setTimeHorizon] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const [saveMessage, setSaveMessage] = useState<string | null>(null)
  const [renamingId, setRenamingId] = useState<string | null>(null)
  const [renameValue, setRenameValue] = useState('')

  useEffect(() => {
    const load = async () => {
      try {
        const meData = await getMe()
        const sessionData = await getChatSessions()
        const prefsData = await getPreferences(getSessionId())

        const prefs: UserPreferences = prefsData.preferences || {}
        setMe(meData)
        setSessions(sessionData.sessions || [])
        setPreferences(prefs)
        setGoals(formatPreferenceValue(prefs.goals) === 'Not set' ? '' : formatPreferenceValue(prefs.goals))
        setRiskLevel(prefs.risk_level || '')
        setLanguage(prefs.language || '')
        setTimeHorizon(prefs.time_horizon || '')
      } catch {
        setError('Please log in to view your profile and chats.')
      }
    }
    load()
  }, [])

  const handleSavePreferences = async () => {
    setSaving(true)
    setSaveMessage(null)
    try {
      const sessionId = getSessionId()
      await savePreference(sessionId, 'goals', goals.trim())
      await savePreference(sessionId, 'risk_level', riskLevel)
      await savePreference(sessionId, 'language', language)
      if (timeHorizon.trim()) {
        await savePreference(sessionId, 'time_horizon', timeHorizon.trim())
      }

      const prefsData = await getPreferences(sessionId)
      setPreferences(prefsData.preferences || {})
      setSaveMessage('Financial profile saved. The advisor will use these in future chats.')
    } catch {
      setSaveMessage('Could not save your profile. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <main className="min-h-screen flex flex-col">
      <Header />
      <div className="max-w-5xl mx-auto px-4 py-6 w-full">
        <h2 className="text-xl font-semibold text-gray-900">My Profile</h2>
        <p className="text-sm text-gray-600 mt-1">
          Your account, financial preferences, and chat history.
        </p>

        {error && <div className="mt-4 text-sm text-gray-600">{error}</div>}

        {!error && (
          <div className="mt-6 space-y-6">
            <div className="rounded border border-gray-200 p-4 bg-white">
              <div className="text-sm text-gray-600">Email</div>
              <div className="font-medium">{me?.email}</div>
              {me?.full_name && (
                <>
                  <div className="text-sm text-gray-600 mt-2">Name</div>
                  <div className="font-medium">{me.full_name}</div>
                </>
              )}
            </div>

            <div className="rounded border border-gray-200 p-4 bg-white">
              <div className="font-medium text-gray-900">Financial Profile</div>
              <p className="text-sm text-gray-600 mt-1">
                Saved to your long-term profile and used to personalize advice.
              </p>

              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                <div>
                  <div className="text-xs text-gray-500 uppercase tracking-wide">Financial goals</div>
                  <div className="text-sm font-medium mt-0.5">
                    {formatPreferenceValue(preferences.goals)}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-500 uppercase tracking-wide">Risk tolerance</div>
                  <div className="text-sm font-medium mt-0.5 capitalize">
                    {formatPreferenceValue(preferences.risk_level)}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-500 uppercase tracking-wide">Language</div>
                  <div className="text-sm font-medium mt-0.5">
                    {formatPreferenceValue(preferences.language)}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-500 uppercase tracking-wide">Time horizon</div>
                  <div className="text-sm font-medium mt-0.5">
                    {formatPreferenceValue(preferences.time_horizon)}
                  </div>
                </div>
              </div>

              <div className="mt-5 pt-4 border-t border-gray-100 space-y-3">
                <div>
                  <label className="block text-sm text-gray-700 mb-1">Financial goals</label>
                  <input
                    type="text"
                    value={goals}
                    onChange={(e) => setGoals(e.target.value)}
                    placeholder="e.g. emergency fund, buy land, retirement"
                    className="w-full border border-gray-300 rounded px-3 py-2 text-sm bg-white text-gray-900"
                  />
                </div>
                <div className="grid gap-3 sm:grid-cols-2">
                  <div>
                    <label className="block text-sm text-gray-700 mb-1">Risk tolerance</label>
                    <select
                      value={riskLevel}
                      onChange={(e) => setRiskLevel(e.target.value)}
                      className="w-full border border-gray-300 rounded px-3 py-2 text-sm bg-white text-gray-900"
                    >
                      <option value="">Select...</option>
                      <option value="low">Low — safety first</option>
                      <option value="medium">Medium — balanced</option>
                      <option value="high">High — growth focused</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm text-gray-700 mb-1">Preferred language</label>
                    <select
                      value={language}
                      onChange={(e) => setLanguage(e.target.value)}
                      className="w-full border border-gray-300 rounded px-3 py-2 text-sm bg-white text-gray-900"
                    >
                      <option value="">Select...</option>
                      <option value="english">English</option>
                      <option value="kiswahili">Kiswahili</option>
                      <option value="mixed">English / Kiswahili mix</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-sm text-gray-700 mb-1">Time horizon (optional)</label>
                  <input
                    type="text"
                    value={timeHorizon}
                    onChange={(e) => setTimeHorizon(e.target.value)}
                    placeholder="e.g. 1 year, 5+ years"
                    className="w-full border border-gray-300 rounded px-3 py-2 text-sm bg-white text-gray-900"
                  />
                </div>
                <button
                  onClick={handleSavePreferences}
                  disabled={saving}
                  className="px-4 py-2 text-sm rounded bg-primary-600 text-white hover:bg-primary-700 disabled:opacity-50"
                >
                  {saving ? 'Saving...' : 'Save financial profile'}
                </button>
                {saveMessage && (
                  <p className="text-sm text-gray-600">{saveMessage}</p>
                )}
              </div>
            </div>

            <div className="rounded border border-gray-200 p-4 bg-white">
              <div className="font-medium">My Chats</div>
              <div className="mt-3 space-y-3">
                {sessions.length === 0 && (
                  <div className="text-sm text-gray-600">No sessions found.</div>
                )}
                {sessions.map((session) => (
                  <div key={session.session_id} className="border border-gray-200 rounded p-3">
                    <div className="text-sm text-gray-700">
                      {session.title || session.summary || session.last_message}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      Last updated: {session.last_updated}
                    </div>
                    <div className="text-sm text-gray-600 mt-2">
                      {session.last_role}: {session.last_message}
                    </div>
                    <div className="mt-3 flex items-center space-x-2">
                      <ExportButton sessionId={session.session_id} format="csv" />
                      {renamingId === session.session_id ? (
                        <div className="flex items-center space-x-2">
                          <input
                            type="text"
                            value={renameValue}
                            onChange={(e) => setRenameValue(e.target.value)}
                            className="border border-gray-300 rounded px-2 py-1 text-xs"
                          />
                          <button
                            onClick={async () => {
                              await renameChat(session.session_id, renameValue)
                              setRenamingId(null)
                              setRenameValue('')
                              const data = await getChatSessions()
                              setSessions(data.sessions || [])
                            }}
                            className="text-xs text-primary-600"
                          >
                            Save
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => {
                            setRenamingId(session.session_id)
                            setRenameValue(session.title || session.summary || session.last_message)
                          }}
                          className="text-xs text-gray-600 hover:text-gray-900"
                        >
                          Rename
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </main>
  )
}

function ExportButton({ sessionId, format }: { sessionId: string; format: 'csv' }) {
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
