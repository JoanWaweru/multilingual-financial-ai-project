export type UserRole = 'user' | 'admin' | 'moderator'

export function isStaffRole(role?: string | null): boolean {
  return role === 'admin' || role === 'moderator'
}
