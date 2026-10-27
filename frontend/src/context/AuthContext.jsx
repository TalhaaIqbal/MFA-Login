import { createContext, useContext, useState, useEffect } from 'react'
import api from '../utils/api'

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [pending2FA, setPending2FA] = useState(false)
  const [tempToken, setTempToken] = useState(null)
  const [pendingUserId, setPendingUserId] = useState(null)
  const [mfaMethod, setMfaMethod] = useState('totp')
 

  useEffect(() => {
    const verifySession = async () => {
      try {
        const response = await api.get('/auth/me')
        setUser(response.data.data)
        localStorage.setItem('user', JSON.stringify(response.data.data))
      } catch (err) {
        // Only a 401 means "not logged in"; keep local user on network hiccups
        if (err.response?.status === 401) {
          localStorage.removeItem('user')
          setUser(null)
        } else {
          const cached = localStorage.getItem('user')
          if (cached) setUser(JSON.parse(cached))
        }
      } finally {
        setLoading(false)
      }
    }

    verifySession()
  }, [])

  const login = (userData) => {
    setUser(userData)
    localStorage.setItem('user', JSON.stringify(userData))
  }

  const logout = async () => {
    try {
      // Call backend logout to clear HttpOnly cookies
      await api.post('/auth/logout')
    } catch (err) {
      // Continue with local logout even if backend fails
      console.error('Logout error:', err)
    } finally {
      // Clear local state
      setUser(null)
      localStorage.removeItem('user')
      setPending2FA(false)
      setTempToken(null)
      setPendingUserId(null)
    }
  }

  const setPending2FAData = (tempToken, userId, method = 'totp') => {
    setMfaMethod(method)
    setPending2FA(true)
    setTempToken(tempToken)
    setPendingUserId(userId)
    // Store in sessionStorage for page refresh handling
    sessionStorage.setItem('pending2FA', JSON.stringify({ tempToken, userId, method }))
  }

  const clearPending2FA = () => {
    setPending2FA(false)
    setTempToken(null)
    setPendingUserId(null)
    sessionStorage.removeItem('pending2FA')
  }

  const verify2FA = async (code) => {
    try {
      const isEmail = mfaMethod === 'email'
      const response = await api.post(
        isEmail ? '/auth/email-otp/verify' : '/auth/2fa/verify',
        { code },
        { headers: { [isEmail ? 'X-Email-OTP-Token' : 'X-2FA-Token']: tempToken } }
      )

      if (response.data.data && response.data.data.user_details) {
        login(response.data.data.user_details)
        clearPending2FA()
        return { success: true }
      }
      return { success: false, message: 'Invalid response from server' }
    } catch (err) {
      return { success: false, message: err.response?.data?.message || '2FA verification failed' }
    }
  }

  const isAuthenticated = () => {
    return !!user
  }

  const refreshUser = async () => {
    try {
      const response = await api.get('/auth/me')
      setUser(response.data.data)
      localStorage.setItem('user', JSON.stringify(response.data.data))
      return response.data.data
    } catch (err) {
      localStorage.removeItem('user')
      setUser(null)
      throw err
    }
  }

  const isAdmin = () => {
    return user?.role === 'admin'
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, isAuthenticated, loading, pending2FA, tempToken, pendingUserId, mfaMethod, setPending2FAData, clearPending2FA, verify2FA, refreshUser, isAdmin }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
