'use client'

import { useEffect, useState } from 'react'
import { getMe, loginUser, registerUser } from '@/lib/api'

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
    <div className="flex items-center space-x-2 text-sm">
      {isRegister && (
        <input
          type="text"
          placeholder="Full name"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          className="border border-gray-300 rounded px-2 py-1 text-xs"
        />
      )}
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className="border border-gray-300 rounded px-2 py-1 text-xs"
      />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className="border border-gray-300 rounded px-2 py-1 text-xs"
      />
      <button
        onClick={handleAuth}
        disabled={loading || !email || !password}
        className="px-3 py-1 text-xs rounded bg-primary-600 text-white disabled:opacity-50"
      >
        {isRegister ? 'Register' : 'Login'}
      </button>
      <button
        onClick={() => setIsRegister(!isRegister)}
        className="px-2 py-1 text-xs text-gray-600 hover:text-gray-900"
      >
        {isRegister ? 'Have account?' : 'Create account'}
      </button>
      {error && <span className="text-xs text-red-600">{error}</span>}
    </div>
  )
}
