import { useCallback, useEffect, useMemo, useState } from 'react'
import AuthContext from './auth-context.js'
import api from '../lib/api'

/**
 * Holds the session for the whole app.
 *
 * Every route used to re-fetch the session on mount (Profile even hit a route
 * that does not exist), so navigating re-ran the same requests over and over.
 * They run once here instead.
 */
export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null)
  const [currentRecruiter, setCurrentRecruiter] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const controller = new AbortController()
    Promise.all([
      api.get('/get-session-user', { signal: controller.signal }).catch(() => null),
      api.get('/get-session-recruiter', { signal: controller.signal }).catch(() => null),
    ])
      .then(([user, recruiter]) => {
        if (controller.signal.aborted) return
        if (user?.id) setCurrentUser(user)
        if (recruiter?.id) setCurrentRecruiter(recruiter)
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false)
      })
    return () => controller.abort()
  }, [])

  const logoutUser = useCallback(async () => {
    setCurrentUser(null)
    await api.del('/logout').catch(() => {})
  }, [])

  const logoutRecruiter = useCallback(async () => {
    setCurrentRecruiter(null)
    await api.del('/recruiters-logout').catch(() => {})
  }, [])

  const value = useMemo(
    () => ({
      currentUser, setCurrentUser,
      currentRecruiter, setCurrentRecruiter,
      logoutUser, logoutRecruiter,
      loading,
    }),
    [currentUser, currentRecruiter, logoutUser, logoutRecruiter, loading],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
