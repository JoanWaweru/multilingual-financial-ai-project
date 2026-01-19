'use client'

import { useEffect, useState } from 'react'
import { getAdminOverview, getAdminFeedback } from '@/lib/api'

export default function AdminPage() {
  const [overview, setOverview] = useState<any>(null)
  const [feedback, setFeedback] = useState<any[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const load = async () => {
      try {
        const overviewData = await getAdminOverview()
        const feedbackData = await getAdminFeedback()
        setOverview(overviewData)
        setFeedback(feedbackData.feedback || [])
      } catch {
        setError('Admin access required.')
      }
    }
    load()
  }, [])

  return (
    <div className="max-w-5xl mx-auto px-4 py-6">
      <h2 className="text-xl font-semibold text-gray-900">Admin Dashboard</h2>
      {error && <div className="mt-4 text-sm text-gray-600">{error}</div>}

      {!error && overview && (
        <div className="mt-6 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <StatCard label="Users" value={overview.users} />
            <StatCard label="Messages" value={overview.messages} />
            <StatCard label="Feedback" value={overview.feedback} />
          </div>

          <div className="rounded border border-gray-200 p-4">
            <div className="font-medium">Recent Feedback</div>
            <div className="mt-3 space-y-3">
              {feedback.length === 0 && (
                <div className="text-sm text-gray-600">No feedback yet.</div>
              )}
              {feedback.map((item) => (
                <div key={item.id} className="border border-gray-200 rounded p-3 text-sm">
                  <div>Rating: {item.rating}</div>
                  {item.comment && <div className="mt-1 text-gray-600">{item.comment}</div>}
                  <div className="mt-1 text-xs text-gray-500">
                    {item.created_at}
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

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded border border-gray-200 p-4">
      <div className="text-sm text-gray-600">{label}</div>
      <div className="text-2xl font-semibold">{value}</div>
    </div>
  )
}
