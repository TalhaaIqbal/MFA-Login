import { Navigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-800 to-gray-600">
        <div className="text-white text-xl">Loading...</div>
      </div>
    )
  }

  if (isAuthenticated()) {
    return <Navigate to="/dashboard" replace />
  }

  return children
}

export default PublicRoute
