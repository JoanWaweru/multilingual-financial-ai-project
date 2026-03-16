'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Header from '@/components/Header'
import { registerUser } from '@/lib/api'

export default function RegisterPage() {
  const router = useRouter()
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const res = await registerUser(email, password, fullName || undefined)
      localStorage.setItem('auth_token', res.access_token)
      router.push('/')
    } catch (err) {
      setError('Registration failed. Please check your details and try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen flex flex-col">
      <Header />
      <div className="flex-1 flex flex-col items-center justify-center px-4">
        <div className="w-full max-w-md rounded-lg bg-white shadow-md border border-gray-200 p-6 space-y-4">
          <h1 className="text-lg font-semibold text-gray-900">Create account</h1>
          <form onSubmit={handleSubmit} className="space-y-3 text-sm">
            <div className="space-y-1">
              <label className="block text-gray-700">Full name (optional)</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full border border-gray-300 rounded px-2 py-1 bg-white text-gray-900 placeholder:text-gray-500"
                placeholder="Jane Doe"
              />
            </div>
            <div className="space-y-1">
              <label className="block text-gray-700">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full border border-gray-300 rounded px-2 py-1 bg-white text-gray-900 placeholder:text-gray-500"
                placeholder="you@example.com"
                required
              />
            </div>
            <div className="space-y-1">
              <label className="block text-gray-700">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full border border-gray-300 rounded px-2 py-1 bg-white text-gray-900 placeholder:text-gray-500"
                required
              />
            </div>
            {error && <p className="text-xs text-red-600">{error}</p>}
            <button
              type="submit"
              disabled={loading || !email || !password}
              className="w-full mt-2 px-3 py-2 rounded bg-primary-600 text-white text-sm disabled:opacity-50"
            >
              {loading ? 'Creating account...' : 'Register'}
            </button>
          </form>
          <p className="text-xs text-gray-600">
            Already have an account?{' '}
            <button
              type="button"
              onClick={() => router.push('/login')}
              className="text-primary-600 hover:text-primary-700 underline"
            >
              Login
            </button>
          </p>
        </div>
      </div>
    </main>
  )
}

