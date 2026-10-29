import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import api from '../utils/api'

function VerifyEmail() {
  const [searchParams] = useSearchParams()
  const [status, setStatus] = useState('loading') // loading, success, error
  const [message, setMessage] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    const verifyEmail = async () => {
      const token = searchParams.get('token')

      if (!token) {
        setStatus('error')
        setMessage('Invalid verification link. No token provided.')
        return
      }

      try {
        const response = await api.get(`/auth/verify-email?token=${token}`)

        if (response.data.message) {
          setStatus('success')
          setMessage(response.data.message)
        } else {
          throw new Error('Invalid response from server')
        }
      } catch (err) {
        console.error('Email verification error:', err)
        setStatus('error')
        setMessage(err.response?.data?.message || 'Failed to verify email. The link may be expired or invalid.')
      }
    }

    verifyEmail()
  }, [searchParams])

  const handleGoToLogin = () => {
    navigate('/login')
  }

  return (
    <>
      <Helmet>
        <title>Verify Email | Scraper Dashboard</title>
      </Helmet>

      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-800 to-gray-600 p-4">
        <div className="bg-white rounded-xl p-10 w-full max-w-md shadow-2xl text-center">
          {status === 'loading' && (
            <>
              <div className="flex justify-center mb-6">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500"></div>
              </div>
              <h1 className="text-2xl font-semibold text-gray-800 mb-2">Verifying Email...</h1>
              <p className="text-gray-500 text-sm">Please wait while we verify your email address.</p>
            </>
          )}

          {status === 'success' && (
            <>
              <div className="flex justify-center mb-6">
                <svg className="w-16 h-16 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h1 className="text-2xl font-semibold text-gray-800 mb-2">Email Verified!</h1>
              <p className="text-gray-500 text-sm mb-6">{message}</p>
              <button
                onClick={handleGoToLogin}
                className="w-full bg-emerald-500 text-white py-3 rounded-lg font-semibold hover:bg-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-300 transition-all"
              >
                Go to Login
              </button>
            </>
          )}

          {status === 'error' && (
            <>
              <div className="flex justify-center mb-6">
                <svg className="w-16 h-16 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h1 className="text-2xl font-semibold text-gray-800 mb-2">Verification Failed</h1>
              <p className="text-gray-500 text-sm mb-6">{message}</p>
              <button
                onClick={handleGoToLogin}
                className="w-full bg-gray-500 text-white py-3 rounded-lg font-semibold hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-300 transition-all"
              >
                Go to Login
              </button>
            </>
          )}
        </div>
      </div>
    </>
  )
}

export default VerifyEmail
