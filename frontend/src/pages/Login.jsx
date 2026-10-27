import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import api from '../utils/api'
import { useAuth } from '../context/AuthContext'
import logger from '../utils/logger'

function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [show2FAInput, setShow2FAInput] = useState(false)
  const [twoFactorCode, setTwoFactorCode] = useState('')
  const navigate = useNavigate()
  const { login, pending2FA, setPending2FAData, clearPending2FA, verify2FA } = useAuth()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await api.post('/auth/login', { email, password }, { withCredentials: true })

      if (response.data.data.requires_2fa) {
        // 2FA is required, show verification input
        setPending2FAData(response.data.data.temp_token, response.data.data.user_id)
        setShow2FAInput(true)
        setLoading(false)
      } else if (response.data.data && response.data.data.user_details) {
        // No 2FA, proceed with normal login
        login(response.data.data.user_details)
        navigate('/dashboard', { replace: true })
      } else {
        throw new Error('Invalid response from server')
      }
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  const handle2FAVerify = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const result = await verify2FA(twoFactorCode)

      if (result.success) {
        navigate('/dashboard', { replace: true })
      } else {
        setError(result.message)
      }
    } catch (err) {
      setError(err.response?.data?.message || '2FA verification failed')
    } finally {
      setLoading(false)
    }
  }

  const handleCancel2FA = () => {
    setShow2FAInput(false)
    setTwoFactorCode('')
    clearPending2FA()
    setError('')
    setEmail('')
    setPassword('')
  }

  return (
    <>
      <Helmet>
        <title>Login | Scraper Dashboard</title>
        <meta name="description" content="Sign in to your Scraper Dashboard account to manage your web scrapers and data." />
      </Helmet>

      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-800 to-gray-600 p-4">
      <div className="bg-white rounded-xl p-10 w-full max-w-md shadow-2xl">
        <h1 className="text-3xl font-semibold text-gray-800 mb-2">Scraper Dashboard</h1>
        <p className="text-gray-500 text-sm mb-8">{show2FAInput ? 'Enter 2FA code' : 'Sign in to your account'}</p>

        {!show2FAInput ? (
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value)
                  setError('')
                }}
                placeholder="Enter your email"
                required
                className={`w-full px-4 py-3 border-2 rounded-lg focus:outline-none focus:ring-2 transition-all text-gray-800 placeholder-gray-400 ${
                  error && !email
                    ? 'border-red-500 focus:border-red-500 focus:ring-red-100'
                    : 'border-gray-200 focus:border-emerald-500 focus:ring-emerald-100'
                }`}
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value)
                  setError('')
                }}
                placeholder="Enter your password"
                required
                className={`w-full px-4 py-3 border-2 rounded-lg focus:outline-none focus:ring-2 transition-all text-gray-800 placeholder-gray-400 ${
                  error && !password
                    ? 'border-red-500 focus:border-red-500 focus:ring-red-100'
                    : 'border-gray-200 focus:border-emerald-500 focus:ring-emerald-100'
                }`}
              />
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-emerald-500 text-white py-3 rounded-lg font-semibold hover:bg-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-300 transition-all disabled:opacity-60 disabled:cursor-not-allowed mt-2"
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span className="ml-2">Signing in...</span>
                </div>
              ) : 'Sign In'}
            </button>
          </form>
        ) : (
          <form onSubmit={handle2FAVerify} className="space-y-5">
            <div>
              <label htmlFor="twoFactorCode" className="block text-sm font-medium text-gray-700 mb-2">
                2FA Code
              </label>
              <input
                id="twoFactorCode"
                type="text"
                value={twoFactorCode}
                onChange={(e) => {
                  setTwoFactorCode(e.target.value)
                  setError('')
                }}
                placeholder="Enter 6-digit code"
                maxLength={6}
                required
                className="w-full px-4 py-3 border-2 rounded-lg focus:outline-none focus:ring-2 transition-all text-gray-800 placeholder-gray-400 text-center text-lg tracking-widest"
              />
              <p className="text-xs text-gray-500 mt-2 text-center">
                Enter the code from your authenticator app
              </p>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading || twoFactorCode.length !== 6}
              className="w-full bg-emerald-500 text-white py-3 rounded-lg font-semibold hover:bg-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-300 transition-all disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span className="ml-2">Verifying...</span>
                </div>
              ) : 'Verify'}
            </button>

            <button
              type="button"
              onClick={handleCancel2FA}
              className="w-full text-gray-600 hover:text-gray-800 py-2 text-sm"
            >
              Cancel
            </button>
          </form>
        )}

        <div className="mt-6 text-center text-sm text-gray-500">
          <Link to="/privacy-policy" className="text-emerald-600 hover:text-emerald-700">
            Privacy Policy
          </Link>
        </div>
      </div>
    </div>
    </>
  )
}

export default Login
