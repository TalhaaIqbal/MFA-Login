import { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'
import api from '../utils/api'

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [pending2FA, setPending2FA] = useState(false)
  const [tempToken, setTempToken] = useState(null)
  const [pendingUserId, setPendingUserId] = useState(null)
 

  useEffect(() => {
    const verifySession = async () => {
      // Always verify with server to get the actual role from database
      // This prevents role manipulation via localStorage
      try {
        // Use direct axios call without interceptor redirect
        const response = await axios.get(
          `${import.meta.env.VITE_API_URI || 'http://localhost:8000/api/v1'}/auth/me`,
          { withCredentials: true }
        )
        setUser(response.data.data)
        localStorage.setItem('user', JSON.stringify(response.data.data))
      } catch (err) {
        // Session invalid, clear local storage
        localStorage.removeItem('user')
        setUser(null)
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
      await axios.post(
        `${import.meta.env.VITE_API_URI || 'http://localhost:8000/api/v1'}/auth/logout`,
        {},
        { withCredentials: true }
      )
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

  const setPending2FAData = (tempToken, userId) => {
    setPending2FA(true)
    setTempToken(tempToken)
    setPendingUserId(userId)
    // Store in sessionStorage for page refresh handling
    sessionStorage.setItem('pending2FA', JSON.stringify({ tempToken, userId }))
  }

  const clearPending2FA = () => {
    setPending2FA(false)
    setTempToken(null)
    setPendingUserId(null)
    sessionStorage.removeItem('pending2FA')
  }

  const verify2FA = async (code) => {
    try {
      const response = await axios.post(
        `${import.meta.env.VITE_API_URI || 'http://localhost:8000/api/v1'}/auth/2fa/verify`,
        { code },
        {
          headers: {
            'X-2FA-Token': tempToken
          },
          withCredentials: true
        }
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
      const response = await axios.get(
        `${import.meta.env.VITE_API_URI || 'http://localhost:8000/api/v1'}/auth/me`,
        { withCredentials: true }
      )
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
    <AuthContext.Provider value={{ user, login, logout, isAuthenticated, loading, pending2FA, tempToken, pendingUserId, setPending2FAData, clearPending2FA, verify2FA, refreshUser, isAdmin }}>
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
