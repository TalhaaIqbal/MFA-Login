import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'
import { useState } from 'react'

function TopNav({ title }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [loggingOut, setLoggingOut] = useState(false)

  const handleLogout = async () => {
    setLoggingOut(true)
    try {
      await logout()
      navigate('/login')
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      setLoggingOut(false)
    }
  }

  return (
    <nav className="bg-gray-900 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-white">{title}</h1>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-white">Welcome, {user?.full_name || user?.email}</span>
            <button
              onClick={handleLogout}
              disabled={loggingOut}
              className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {loggingOut ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span className="ml-2">Logging out...</span>
                </div>
              ) : 'Logout'}
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default TopNav
