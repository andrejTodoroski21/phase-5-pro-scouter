import { useCallback, useEffect, useMemo, useState } from 'react'
import AuthContext from './auth-context.js'
import api from '../lib/api'

/**
 * Holds the session for the whole app.
 *
 * Players and recruiters are one account type now, told apart by `role`, so
 * there is a single `currentUser` instead of the two parallel states this
 * used to carry.
 */
export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const controller = new AbortController()
    api.get('/me', { signal: controller.signal })
      .then((user) => {
        if (!controller.signal.aborted && user?.id) setCurrentUser(user)
      })
      .catch(() => {})
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false)
      })
    return () => controller.abort()
  }, [])

  const logout = useCallback(async () => {
    setCurrentUser(null)
    await api.del('/logout').catch(() => {})
  }, [])

  const value = useMemo(
    () => ({
      currentUser,
      setCurrentUser,
      logout,
      loading,
      isRecruiter: currentUser?.role === 'recruiter',
    }),
    [currentUser, logout, loading],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
