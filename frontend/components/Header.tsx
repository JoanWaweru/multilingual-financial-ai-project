'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'
import { Wallet, Globe } from 'lucide-react'
import AuthControls from './AuthControls'
import { getMe } from '@/lib/api'
import { isStaffRole } from '@/lib/roles'
import { isUnauthorizedError } from '@/lib/auth-session'

type UserInfo = {
  role?: string
}

export default function Header() {
  const [user, setUser] = useState<UserInfo | null>(null)

  useEffect(() => {
    const load = async () => {
      const token = localStorage.getItem('auth_token')
      if (!token) {
        setUser(null)
        return
      }

      try {
        const me = await getMe()
        setUser(me)
      } catch (error) {
        if (isUnauthorizedError(error)) {
          localStorage.removeItem('auth_token')
        }
        setUser(null)
      }
    }
    load()
  }, [])

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-6xl mx-auto px-4 py-4">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="flex items-center space-x-3">
            <Wallet className="w-8 h-8 text-primary-600" />
            <div>
              <h1 className="text-xl md:text-2xl font-bold text-gray-900">
                Kenyan Financial Advisor AI
              </h1>
              <p className="text-xs md:text-sm text-gray-600">
                Personal finance guidance for Kenyans
              </p>
            </div>
          </div>
          <div className="flex w-full flex-col items-start gap-2 md:w-auto md:items-end">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Globe className="w-4 h-4" />
              <span>English / Kiswahili</span>
            </div>
            <div className="flex flex-wrap items-center gap-3 text-xs text-gray-600">
              {user && (
                <Link href="/profile" className="hover:text-gray-900">My Profile</Link>
              )}
              {isStaffRole(user?.role) && (
                <Link href="/documents" className="hover:text-gray-900">Documents</Link>
              )}
              {user?.role === 'admin' && (
                <Link href="/admin" className="hover:text-gray-900">Admin</Link>
              )}
            </div>
            <AuthControls />
          </div>
        </div>
      </div>
    </header>
  )
}
