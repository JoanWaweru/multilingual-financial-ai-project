'use client'

import { useEffect, useState } from 'react'
import { getEvalMetrics } from '@/lib/api'

export default function EvaluationPage() {
  const [metrics, setMetrics] = useState<any[]>([])

  useEffect(() => {
    const load = async () => {
      try {
        const data = await getEvalMetrics()
        setMetrics(data.metrics || [])
      } catch {
        setMetrics([])
      }
    }
    load()
  }, [])

  return (
    <div className="max-w-5xl mx-auto px-4 py-6">
      <h2 className="text-xl font-semibold text-gray-900">Code-Switch Evaluation</h2>
      <p className="text-sm text-gray-600 mt-1">
        Historical metrics from evaluation runs.
      </p>

      <div className="mt-6 space-y-3">
        {metrics.length === 0 && (
          <div className="text-sm text-gray-600">No metrics recorded yet.</div>
        )}
        {metrics.map((entry, idx) => (
          <div key={idx} className="border border-gray-200 rounded p-3 text-sm">
            <div className="text-xs text-gray-500">{entry.timestamp}</div>
            <div className="mt-1">Mode: {entry.mode}</div>
            <div className="mt-1">Accuracy: {entry.metrics?.accuracy}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
