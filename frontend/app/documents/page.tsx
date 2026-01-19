'use client'

import { useState } from 'react'
import { uploadDocument } from '@/lib/api'

export default function DocumentsPage() {
  const [file, setFile] = useState<File | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleUpload = async () => {
    if (!file) return
    setLoading(true)
    setMessage(null)
    try {
      const res = await uploadDocument(file)
      setMessage(res.message || 'Uploaded')
    } catch {
      setMessage('Upload failed. Ensure you are an admin or moderator.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-6">
      <h2 className="text-xl font-semibold text-gray-900">Document Ingestion</h2>
      <p className="text-sm text-gray-600 mt-1">
        Upload documents to update the knowledge base.
      </p>

      <div className="mt-6 border border-gray-200 rounded p-4">
        <input
          type="file"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="text-sm"
        />
        <button
          onClick={handleUpload}
          disabled={!file || loading}
          className="ml-3 px-3 py-1 text-xs rounded bg-primary-600 text-white disabled:opacity-50"
        >
          Upload
        </button>
        {message && <div className="mt-3 text-sm text-gray-600">{message}</div>}
      </div>
    </div>
  )
}
