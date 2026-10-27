import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSearchParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Helmet } from 'react-helmet-async'
import api from '../utils/api'

function OAuthCallback() {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const { refreshUser } = useAuth()

  useEffect(() => {
    const handleOAuthCallback = async () => {
      try {
        // Check if session_id is in query params (for cross-domain OAuth)
        const sessionId = searchParams.get('session_id')

        if (sessionId) {
          // Store session_id as cookie via backend endpoint
          await api.post('/auth/set-session-cookie', { session_id: sessionId })
          // Remove session_id from URL to prevent it from staying in history
          searchParams.delete('session_id')
          setSearchParams(searchParams)
        }

        // Call /auth/me to verify the session and get user data
        await refreshUser()
        // If successful, redirect to dashboard
        navigate('/dashboard', { replace: true })
      } catch (err) {
        console.error('OAuth callback error:', err)
        // If failed, redirect to login with error
        navigate('/login?error=oauth_failed', { replace: true })
      }
    }

    handleOAuthCallback()
  }, [navigate, refreshUser, searchParams, setSearchParams])

  return (
    <>
      <Helmet>
        <title>OAuth Callback | Scraper Dashboard</title>
      </Helmet>
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-800 to-gray-600">
        <div className="flex items-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
          <span className="ml-4 text-white text-xl">Completing sign in...</span>
        </div>
      </div>
    </>
  )
}

export default OAuthCallback
