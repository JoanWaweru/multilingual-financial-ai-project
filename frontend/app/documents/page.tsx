'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Header from '@/components/Header'
import { getMe, uploadDocument } from '@/lib/api'
import { isStaffRole } from '@/lib/roles'

export default function DocumentsPage() {
  const router = useRouter()
  const [file, setFile] = useState<File | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [authorized, setAuthorized] = useState<boolean | null>(null)

  useEffect(() => {
    const checkAccess = async () => {
      try {
        const me = await getMe()
        if (!isStaffRole(me.role)) {
          router.replace('/')
          return
        }
        setAuthorized(true)
      } catch {
        router.replace('/login')
      }
    }
    checkAccess()
  }, [router])

  const handleUpload = async () => {
    if (!file) return
    setLoading(true)
    setMessage(null)
    try {
      const res = await uploadDocument(file)
      setMessage(res.message || 'Uploaded')
      setFile(null)
    } catch {
      setMessage('Upload failed. Only admins and moderators can add documents.')
    } finally {
      setLoading(false)
    }
  }

  if (authorized !== true) {
    return (
      <main className="min-h-screen flex flex-col">
        <Header />
        <div className="max-w-4xl mx-auto px-4 py-6 text-sm text-gray-600">
          Checking access...
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen flex flex-col">
      <Header />
      <div className="max-w-4xl mx-auto px-4 py-6 w-full">
        <h2 className="text-xl font-semibold text-gray-900">Document Ingestion</h2>
        <p className="text-sm text-gray-600 mt-1">
          Upload documents to update the knowledge base. Admins and moderators only.
        </p>

        <div className="mt-6 border border-gray-200 rounded p-4 bg-white">
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
            {loading ? 'Uploading...' : 'Upload'}
          </button>
          {message && <div className="mt-3 text-sm text-gray-600">{message}</div>}
        </div>
      </div>
    </main>
  )
}
