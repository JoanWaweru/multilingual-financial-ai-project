'use client'

import Link from 'next/link'
import { Wallet, Globe } from 'lucide-react'
import AuthControls from './AuthControls'

export default function Header() {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-6xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Wallet className="w-8 h-8 text-primary-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Kenyan Financial Advisor AI
              </h1>
              <p className="text-sm text-gray-600">
                Personal finance guidance for Kenyans
              </p>
            </div>
          </div>
          <div className="flex flex-col items-end space-y-2">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <Globe className="w-4 h-4" />
              <span>English / Kiswahili</span>
            </div>
            <div className="flex items-center space-x-4 text-xs text-gray-600">
              <Link href="/profile" className="hover:text-gray-900">My Profile</Link>
              <Link href="/documents" className="hover:text-gray-900">Documents</Link>
              <Link href="/evaluation" className="hover:text-gray-900">Evaluation</Link>
              <Link href="/admin" className="hover:text-gray-900">Admin</Link>
            </div>
            <AuthControls />
          </div>
        </div>
      </div>
    </header>
  )
}

