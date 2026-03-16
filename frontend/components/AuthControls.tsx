'use client'

import { useEffect, useState } from 'react'
import { getMe, loginUser, registerUser, requestPasswordReset, resetPassword } from '@/lib/api'

interface UserInfo {
  user_id: string
  email: string
  full_name?: string
}

export default function AuthControls() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [isRegister, setIsRegister] = useState(false)
  const [user, setUser] = useState<UserInfo | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [showReset, setShowReset] = useState(false)
  const [resetEmail, setResetEmail] = useState('')
  const [resetToken, setResetToken] = useState('')
  const [resetPasswordValue, setResetPasswordValue] = useState('')
  const [resetInfo, setResetInfo] = useState<string | null>(null)
  const [showModal, setShowModal] = useState(false)

  useEffect(() => {
    const init = async () => {
      const token = localStorage.getItem('auth_token')
      if (!token) return
      try {
        const me = await getMe()
        setUser(me)
      } catch {
        localStorage.removeItem('auth_token')
      }
    }
    init()
  }, [])

  const handleAuth = async () => {
    setLoading(true)
    setError(null)
    try {
      if (isRegister) {
        const res = await registerUser(email, password, fullName || undefined)
        localStorage.setItem('auth_token', res.access_token)
        setUser({ user_id: res.user_id, email: res.email, full_name: res.full_name })
      } else {
        const res = await loginUser(email, password)
        localStorage.setItem('auth_token', res.access_token)
        setUser({ user_id: res.user_id, email: res.email, full_name: res.full_name })
      }
    } catch (err: any) {
      setError('Authentication failed. Check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('auth_token')
    setUser(null)
    setEmail('')
    setPassword('')
    setFullName('')
  }

  const handleRequestReset = async () => {
    setLoading(true)
    setResetInfo(null)
    setError(null)
    try {
      const res = await requestPasswordReset(resetEmail)
      if (res.reset_token) {
        setResetToken(res.reset_token)
        setResetInfo('Reset token generated (dev): copy it and set a new password below.')
      } else {
        setResetInfo(res.message)
      }
    } catch {
      setError('Could not request password reset.')
    } finally {
      setLoading(false)
    }
  }

  const handleResetPassword = async () => {
    setLoading(true)
    setResetInfo(null)
    setError(null)
    try {
      await resetPassword(resetToken, resetPasswordValue)
      setResetInfo('Password reset successful. You can now log in.')
      setShowReset(false)
      setResetEmail('')
      setResetToken('')
      setResetPasswordValue('')
    } catch {
      setError('Password reset failed. Check the token and try again.')
    } finally {
      setLoading(false)
    }
  }

  if (user) {
    return (
      <div className="flex items-center space-x-2 text-sm text-gray-600">
        <span>{user.full_name || user.email}</span>
        <button
          onClick={handleLogout}
          className="px-3 py-1 text-xs rounded border border-gray-300 hover:bg-gray-50"
        >
          Logout
        </button>
      </div>
    )
  }

  return (
    <>
      <button
        onClick={() => setShowModal(true)}
        className="px-3 py-1 text-xs rounded border border-gray-300 bg-white text-gray-700 hover:bg-gray-50"
      >
        Log in / Register
      </button>

      {showModal && (
        <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/40 px-4">
          <div className="w-full max-w-md rounded-lg bg-white shadow-lg p-4 space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-gray-900">
                {isRegister ? 'Create account' : 'Login'}
              </h2>
              <button
                onClick={() => setShowModal(false)}
                className="text-xs text-gray-500 hover:text-gray-800"
              >
                Close
              </button>
            </div>

            <div className="flex flex-col space-y-3 text-sm">
              {isRegister && (
                <input
                  type="text"
                  placeholder="Full name"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="border border-gray-300 rounded px-2 py-1 text-xs bg-white text-gray-900 placeholder:text-gray-500"
                />
              )}
              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="border border-gray-300 rounded px-2 py-1 text-xs bg-white text-gray-900 placeholder:text-gray-500"
              />
              <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="border border-gray-300 rounded px-2 py-1 text-xs bg-white text-gray-900 placeholder:text-gray-500"
              />
              <div className="flex items-center justify-between gap-2">
                <button
                  onClick={handleAuth}
                  disabled={loading || !email || !password}
                  className="px-3 py-1 text-xs rounded bg-primary-600 text-white disabled:opacity-50"
                >
                  {isRegister ? 'Register' : 'Login'}
                </button>
                <button
                  onClick={() => {
                    setIsRegister(!isRegister)
                    setShowReset(false)
                  }}
                  className="px-2 py-1 text-xs text-gray-600 hover:text-gray-900"
                >
                  {isRegister ? 'Have account?' : 'Create account'}
                </button>
                <button
                  onClick={() => setShowReset(!showReset)}
                  className="px-2 py-1 text-xs text-gray-600 hover:text-gray-900"
                >
                  Forgot password?
                </button>
              </div>
            </div>

            {showReset && (
              <div className="mt-2 flex w-full flex-col gap-2 rounded border border-gray-200 bg-white p-2 text-xs">
                <input
                  type="email"
                  placeholder="Email for reset"
                  value={resetEmail}
                  onChange={(e) => setResetEmail(e.target.value)}
                  className="border border-gray-300 rounded px-2 py-1 bg-white text-gray-900 placeholder:text-gray-500"
                />
                <button
                  onClick={handleRequestReset}
                  disabled={loading || !resetEmail}
                  className="px-3 py-1 rounded bg-primary-600 text-white disabled:opacity-50"
                >
                  Send reset token
                </button>
                <input
                  type="text"
                  placeholder="Reset token"
                  value={resetToken}
                  onChange={(e) => setResetToken(e.target.value)}
                  className="border border-gray-300 rounded px-2 py-1 bg-white text-gray-900 placeholder:text-gray-500"
                />
                <input
                  type="password"
                  placeholder="New password"
                  value={resetPasswordValue}
                  onChange={(e) => setResetPasswordValue(e.target.value)}
                  className="border border-gray-300 rounded px-2 py-1 bg-white text-gray-900 placeholder:text-gray-500"
                />
                <button
                  onClick={handleResetPassword}
                  disabled={loading || !resetToken || !resetPasswordValue}
                  className="px-3 py-1 rounded bg-primary-600 text-white disabled:opacity-50"
                >
                  Reset password
                </button>
              </div>
            )}

            {resetInfo && <span className="text-xs text-gray-600">{resetInfo}</span>}
            {error && <span className="text-xs text-red-600">{error}</span>}
          </div>
        </div>
      )}
    </>
  )
}
