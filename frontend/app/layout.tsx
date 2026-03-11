import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Kenyan Financial Advisor AI',
  description: 'Conversational AI for personal finance advice in Kenya',
  applicationName: 'Kenyan Financial Advisor AI',
  manifest: '/manifest.json',
  themeColor: '#1d4ed8',
  appleWebApp: {
    capable: true,
    title: 'Kenyan Financial Advisor AI',
    statusBarStyle: 'default',
  },
  icons: {
    icon: ['/favicon.svg', '/icon.svg'],
    apple: '/icon.svg',
  },
}

export const viewport = {
  themeColor: '#1d4ed8',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} min-h-screen bg-slate-50 text-gray-900 antialiased`}>
        {children}
      </body>
    </html>
  )
}

