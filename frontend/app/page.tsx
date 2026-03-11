'use client'

import { useState, useRef, useEffect } from 'react'
import ChatInterface from '@/components/ChatInterface'
import Header from '@/components/Header'

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col">
      <Header />
      <div className="flex-1 flex flex-col max-w-6xl w-full mx-auto px-4 py-4 md:py-6">
        <ChatInterface />
      </div>
    </main>
  )
}

