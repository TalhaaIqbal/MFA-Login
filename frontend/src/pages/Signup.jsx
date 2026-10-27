import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import api from '../utils/api'
import { useAuth } from '../context/AuthContext'
import logger from '../utils/logger'

function Signup() {
  const [email, setEmail] = useState('')
  const [name, setName] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { login } = useAuth()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    // Validate passwords match
    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    // Validate password strength
    const passwordRequirements = [
      { test: password.length >= 8, message: 'Password must be at least 8 characters long' },
      { test: /[A-Z]/.test(password), message: 'Password must contain at least one uppercase letter' },
      { test: /[a-z]/.test(password), message: 'Password must contain at least one lowercase letter' },
      { test: /\d/.test(password), message: 'Password must contain at least one number' },
      { test: /[!@#$%^&*(),.?":{}|<>]/.test(password), message: 'Password must contain at least one special character' }
    ]

    for (const req of passwordRequirements) {
      if (!req.test) {
        setError(req.message)
        return
      }
    }

    setLoading(true)

    try {
      const response = await api.post('/auth/signup', { email, name, password }, { withCredentials: true })

      if (response.data.data && response.data.data.user_details) {
        // Auto-login after successful signup
        login(response.data.data.user_details)
        navigate('/dashboard', { replace: true })
      } else {
        throw new Error('Invalid response from server')
      }
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Signup failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Helmet>
        <title>Sign Up | Scraper Dashboard</title>
        <meta name="description" content="Create a new Scraper Dashboard account to manage your web scrapers and data." />
      </Helmet>

      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-800 to-gray-600 p-4">
      <div className="bg-white rounded-xl p-10 w-full max-w-md shadow-2xl">
        <h1 className="text-3xl font-semibold text-gray-800 mb-2">Create Account</h1>
        <p className="text-gray-500 text-sm mb-8">Sign up to get started</p>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
              Full Name
            </label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => {
                setName(e.target.value)
                setError('')
              }}
              placeholder="Enter your full name"
              required
              className={`w-full px-4 py-3 border-2 rounded-lg focus:outline-none focus:ring-2 transition-all text-gray-800 placeholder-gray-400 ${
                error && !name
                  ? 'border-red-500 focus:border-red-500 focus:ring-red-100'
                  : 'border-gray-200 focus:border-emerald-500 focus:ring-emerald-100'
              }`}
            />
          </div>

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
              placeholder="Create a password"
              required
              className={`w-full px-4 py-3 border-2 rounded-lg focus:outline-none focus:ring-2 transition-all text-gray-800 placeholder-gray-400 ${
                error && !password
                  ? 'border-red-500 focus:border-red-500 focus:ring-red-100'
                  : 'border-gray-200 focus:border-emerald-500 focus:ring-emerald-100'
              }`}
            />
            <p className="text-xs text-gray-500 mt-2">
              Must be at least 8 characters with uppercase, lowercase, number, and special character
            </p>
          </div>

          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
              Confirm Password
            </label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => {
                setConfirmPassword(e.target.value)
                setError('')
              }}
              placeholder="Confirm your password"
              required
              className={`w-full px-4 py-3 border-2 rounded-lg focus:outline-none focus:ring-2 transition-all text-gray-800 placeholder-gray-400 ${
                error && confirmPassword && confirmPassword !== password
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
                <span className="ml-2">Creating account...</span>
              </div>
            ) : 'Sign Up'}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-gray-500">
          Already have an account?{' '}
          <Link to="/login" className="text-emerald-600 hover:text-emerald-700 font-medium">
            Sign in
          </Link>
        </div>

        <div className="mt-4 text-center text-sm text-gray-500">
          <Link to="/privacy-policy" className="text-emerald-600 hover:text-emerald-700">
            Privacy Policy
          </Link>
        </div>
      </div>
    </div>
    </>
  )
}

export default Signup
