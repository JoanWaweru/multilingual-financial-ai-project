'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Header from '@/components/Header'
import { requestPasswordReset, resetPassword } from '@/lib/api'

export default function ForgotPasswordPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [resetToken, setResetToken] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [info, setInfo] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleRequestToken = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setInfo(null)
    try {
      const res = await requestPasswordReset(email)
      setInfo(res.message || 'If this email exists, a reset token has been generated.')
      if (res.reset_token) {
        setResetToken(res.reset_token)
      }
    } catch (err) {
      setError('Could not request password reset. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setInfo(null)
    try {
      await resetPassword(resetToken, newPassword)
      setInfo('Password reset successful. You can now log in.')
      setTimeout(() => router.push('/login'), 1500)
    } catch (err) {
      setError('Password reset failed. Check the token and try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen flex flex-col">
      <Header />
      <div className="flex-1 flex flex-col items-center justify-center px-4">
        <div className="w-full max-w-md rounded-lg bg-white shadow-md border border-gray-200 p-6 space-y-4">
          <h1 className="text-lg font-semibold text-gray-900">Forgot password</h1>

          <form onSubmit={handleRequestToken} className="space-y-3 text-sm">
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
            <button
              type="submit"
              disabled={loading || !email}
              className="w-full mt-1 px-3 py-2 rounded bg-primary-600 text-white text-sm disabled:opacity-50"
            >
              {loading ? 'Requesting token...' : 'Send reset token'}
            </button>
          </form>

          <form onSubmit={handleResetPassword} className="space-y-3 text-sm pt-2 border-t border-gray-200">
            <div className="space-y-1">
              <label className="block text-gray-700">Reset token</label>
              <input
                type="text"
                value={resetToken}
                onChange={(e) => setResetToken(e.target.value)}
                className="w-full border border-gray-300 rounded px-2 py-1 bg-white text-gray-900 placeholder:text-gray-500"
                required
              />
            </div>
            <div className="space-y-1">
              <label className="block text-gray-700">New password</label>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="w-full border border-gray-300 rounded px-2 py-1 bg-white text-gray-900 placeholder:text-gray-500"
                required
              />
            </div>
            <button
              type="submit"
              disabled={loading || !resetToken || !newPassword}
              className="w-full mt-1 px-3 py-2 rounded bg-primary-600 text-white text-sm disabled:opacity-50"
            >
              {loading ? 'Resetting password...' : 'Reset password'}
            </button>
          </form>

          {info && <p className="text-xs text-gray-600">{info}</p>}
          {error && <p className="text-xs text-red-600">{error}</p>}
        </div>
      </div>
    </main>
  )
}

