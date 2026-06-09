import { linkGuestSession } from '@/lib/api'

export async function syncGuestSessionAfterAuth(): Promise<void> {
  if (typeof window === 'undefined') return
  const sessionId = window.localStorage.getItem('kfa_session_id')
  if (!sessionId) return
  try {
    await linkGuestSession(sessionId)
  } catch (error) {
    console.warn('Could not link guest session to account', error)
  }
}

export function isUnauthorizedError(error: unknown): boolean {
  return (
    typeof error === 'object' &&
    error !== null &&
    'response' in error &&
    (error as { response?: { status?: number } }).response?.status === 401
  )
}
