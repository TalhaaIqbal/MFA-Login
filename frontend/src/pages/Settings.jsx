import { useAuth } from '../context/AuthContext'
import Sidebar from '../components/sidebar/Sidebar'
import TopNav from '../components/TopNav'
import { Helmet } from 'react-helmet-async'
import { useState, useEffect } from 'react'
import api from '../utils/api'
import logger from '../utils/logger'

function Settings() {
  const { user, isAdmin } = useAuth()
  const [is2FAEnabled, setIs2FAEnabled] = useState(false)
  const [showQRCode, setShowQRCode] = useState(false)
  const [qrCodeData, setQrCodeData] = useState(null)
  const [verificationCode, setVerificationCode] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [showDisableModal, setShowDisableModal] = useState(false)
  const [disablePassword, setDisablePassword] = useState('')
  const [disableTotpCode, setDisableTotpCode] = useState('')

  // Config state
  const [config, setConfig] = useState({
    file_upload: { max_size: 0 },
    allowed_users: []
  })
  const [configError, setConfigError] = useState('')
  const [configLoading, setConfigLoading] = useState(false)
  const [showConfig, setShowConfig] = useState(false)
  const [newUserEmail, setNewUserEmail] = useState('')

  useEffect(() => {
    // Initialize 2FA status from user data if available
    if (user && user.is_2fa_enabled !== undefined) {
      setIs2FAEnabled(user.is_2fa_enabled)
    } else {
      // Fetch from API if not available
      fetch2FAStatus()
    }
    // Only fetch config if user is admin
    if (isAdmin()) {
      fetchConfig()
    }
  }, [user, isAdmin])

  const fetch2FAStatus = async () => {
    try {
      const response = await api.get('/auth/me')
      setIs2FAEnabled(response.data.data.is_2fa_enabled || false)
    } catch (err) {
      logger.error('Error fetching 2FA status:', err)
    }
  }

  const setup2FA = async () => {
    setError('')
    setSuccess('')
    setLoading(true)

    try {
      const response = await api.post('/auth/2fa/setup', {})
      setQrCodeData(response.data.data)
      setShowQRCode(true)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to setup 2FA')
    } finally {
      setLoading(false)
    }
  }

  const enable2FA = async () => {
    setError('')
    setSuccess('')
    setLoading(true)

    try {
      logger.log('Enabling 2FA with code:', verificationCode, 'challenge_id:', qrCodeData?.challenge_id)
      const response = await api.post('/auth/2fa/enable', {
        code: verificationCode,
        challenge_id: qrCodeData.challenge_id
      })
      logger.log('2FA enable response:', response.data)
      setSuccess('2FA enabled successfully!')
      setIs2FAEnabled(true)
      setShowQRCode(false)
      setVerificationCode('')
      setQrCodeData(null)
    } catch (err) {
      logger.error('Failed to enable 2FA:', err)
      setError(err.response?.data?.message || 'Failed to enable 2FA')
    } finally {
      setLoading(false)
    }
  }

  const disable2FA = async () => {
    setShowDisableModal(true)
  }

  const confirmDisable2FA = async () => {
    if (!disablePassword && !disableTotpCode) {
      setError('Please provide either your password or TOTP code to disable 2FA')
      return
    }

    setError('')
    setSuccess('')
    setLoading(true)

    try {
      await api.post('/auth/2fa/disable', {
        password: disablePassword || undefined,
        totp_code: disableTotpCode || undefined
      })
      setSuccess('2FA disabled successfully!')
      setIs2FAEnabled(false)
      setShowDisableModal(false)
      setDisablePassword('')
      setDisableTotpCode('')
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to disable 2FA')
    } finally {
      setLoading(false)
    }
  }

  const cancelDisable2FA = () => {
    setShowDisableModal(false)
    setDisablePassword('')
    setDisableTotpCode('')
    setError('')
  }

  const fetchConfig = async () => {
    // Only fetch if user is admin
    if (!isAdmin()) {
      return
    }

    try {
      const response = await api.get('/config')
      setConfig(response.data.data)
    } catch (err) {
      logger.error('Error fetching config:', err)
      if (err.response?.status === 403) {
        logger.log('User is not authorized to access config')
      } else {
        setError('Failed to load configuration')
      }
    }
  }

  const updateFileUploadConfig = async () => {
    // Check if user is admin
    if (!isAdmin()) {
      setError('Only admin users can update configuration')
      setTimeout(() => setError(''), 3000)
      return
    }

    // Validation
    if (!config.file_upload.max_size || config.file_upload.max_size <= 0) {
      setConfigError('Max file size must be greater than 0')
      setTimeout(() => setConfigError(''), 3000)
      return
    }

    if (config.file_upload.max_size > 100 * 1024 * 1024) { // 100 MB limit
      setConfigError('Max file size cannot exceed 100 MB')
      setTimeout(() => setConfigError(''), 3000)
      return
    }

    setConfigLoading(true)
    try {
      await api.put('/config/file-upload', {
        max_size: config.file_upload.max_size
      })
      setSuccess('File upload configuration updated successfully!')
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to update configuration')
      setTimeout(() => setError(''), 3000)
    } finally {
      setConfigLoading(false)
    }
  }

  const updateAllowedUsersConfig = async (updatedUsers) => {
    // Check if user is admin
    if (!isAdmin()) {
      setError('Only admin users can update configuration')
      setTimeout(() => setError(''), 3000)
      return
    }

    try {
      await api.put('/config/allowed-users', {
        allowed_users: updatedUsers
      })
      setSuccess('Allowed users updated successfully!')
      setTimeout(() => setSuccess(''), 2000)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to update configuration')
      setTimeout(() => setError(''), 3000)
    }
  }

  const addUser = async () => {
    const email = newUserEmail.trim().toLowerCase()
    if (!email) return

    if (config.allowed_users.includes(email)) {
      setError('User already exists in the list')
      setTimeout(() => setError(''), 3000)
      return
    }

    const updatedUsers = [...config.allowed_users, email]
    setConfig({
      ...config,
      allowed_users: updatedUsers
    })
    setNewUserEmail('')

    // Immediately save to database
    await updateAllowedUsersConfig(updatedUsers)
  }

  const removeUser = async (emailToRemove) => {
    const updatedUsers = config.allowed_users.filter(email => email !== emailToRemove)
    setConfig({
      ...config,
      allowed_users: updatedUsers
    })

    // Immediately save to database
    await updateAllowedUsersConfig(updatedUsers)
  }

  return (
    <>
      <Helmet>
        <title>Settings | Scraper Dashboard</title>
        <meta name="description" content="Configure your Scraper Dashboard settings and user preferences." />
      </Helmet>

      <div className="flex min-h-screen bg-gradient-to-br from-gray-800 to-gray-600">
      <Sidebar />

      <div className="flex-1 flex flex-col">
        <TopNav title="Settings" />

        <div className="flex-1 p-8">
          <div className="bg-white rounded-xl shadow-2xl p-8">
            <h2 className="text-3xl font-semibold text-gray-800 mb-6">Settings</h2>

            {/* 2FA Section */}
            <div className="mb-8">
              <h3 className="text-xl font-semibold text-gray-800 mb-4">Two-Factor Authentication (2FA)</h3>
              <div className="p-6 bg-gray-50 border border-gray-200 rounded-lg">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <p className="text-gray-700 mb-2">
                      {is2FAEnabled ? (
                        <span className="text-green-600 font-semibold">2FA is enabled</span>
                      ) : (
                        <span className="text-orange-600 font-semibold">2FA is disabled</span>
                      )}
                    </p>
                    <p className="text-sm text-gray-500">
                      Add an extra layer of security to your account by enabling 2FA.
                    </p>
                  </div>
                  <button
                    onClick={is2FAEnabled ? disable2FA : setup2FA}
                    disabled={loading}
                    className={`px-6 py-2 rounded-lg font-semibold transition-colors ${
                      is2FAEnabled
                        ? 'bg-red-500 text-white hover:bg-red-600'
                        : 'bg-emerald-500 text-white hover:bg-emerald-600'
                    } disabled:opacity-60 disabled:cursor-not-allowed`}
                  >
                    {loading ? (
                      <div className="flex items-center justify-center">
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                        <span className="ml-2">Processing...</span>
                      </div>
                    ) : is2FAEnabled ? 'Disable 2FA' : 'Enable 2FA'}
                  </button>
                </div>

                {error && (
                  <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm mb-4">
                    {error}
                  </div>
                )}

                {success && (
                  <div className="bg-green-50 border border-green-200 text-green-600 px-4 py-3 rounded-lg text-sm mb-4">
                    {success}
                  </div>
                )}

                {showDisableModal && (
                  <div className="mt-6 border-t border-gray-200 pt-6">
                    <h4 className="text-lg font-semibold text-gray-800 mb-4">Disable 2FA - Step-up Authentication Required</h4>
                    <p className="text-sm text-gray-600 mb-4">
                      For your security, please re-authenticate to disable 2FA. Provide either your password or TOTP code.
                    </p>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Password
                        </label>
                        <input
                          type="password"
                          value={disablePassword}
                          onChange={(e) => setDisablePassword(e.target.value)}
                          placeholder="Enter your password"
                          className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100"
                        />
                      </div>
                      <div className="text-center text-gray-500 text-sm">- OR -</div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          TOTP Code
                        </label>
                        <input
                          type="text"
                          value={disableTotpCode}
                          onChange={(e) => setDisableTotpCode(e.target.value)}
                          placeholder="6-digit code from authenticator app"
                          maxLength={6}
                          className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100"
                        />
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={confirmDisable2FA}
                          disabled={loading || (!disablePassword && !disableTotpCode)}
                          className="flex-1 bg-red-500 text-white py-3 rounded-lg font-semibold hover:bg-red-600 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
                        >
                          {loading ? (
                            <div className="flex items-center justify-center">
                              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                              <span className="ml-2">Disabling...</span>
                            </div>
                          ) : 'Disable 2FA'}
                        </button>
                        <button
                          onClick={cancelDisable2FA}
                          className="flex-1 bg-gray-200 text-gray-700 py-3 rounded-lg font-semibold hover:bg-gray-300 transition-colors"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  </div>
                )}

                {showQRCode && qrCodeData && (
                  <div className="mt-6 border-t border-gray-200 pt-6">
                    <h4 className="text-lg font-semibold text-gray-800 mb-4">Setup 2FA</h4>
                    <div className="flex flex-col items-center">
                      <img
                        src={qrCodeData.qr_code}
                        alt="QR Code"
                        className="mb-4 border border-gray-300 rounded-lg"
                      />
                      <p className="text-sm text-gray-600 mb-4 text-center">
                        Scan this QR code with your authenticator app (Google Authenticator, Authy, etc.)
                      </p>
                      <div className="w-full max-w-sm">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Enter verification code
                        </label>
                        <input
                          type="text"
                          value={verificationCode}
                          onChange={(e) => setVerificationCode(e.target.value)}
                          placeholder="6-digit code"
                          maxLength={6}
                          className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100"
                        />
                        <button
                          onClick={enable2FA}
                          disabled={loading || verificationCode.length !== 6}
                          className="w-full mt-4 bg-emerald-500 text-white py-3 rounded-lg font-semibold hover:bg-emerald-600 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
                        >
                          {loading ? (
                            <div className="flex items-center justify-center">
                              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                              <span className="ml-2">Verifying...</span>
                            </div>
                          ) : 'Enable 2FA'}
                        </button>
                        <button
                          onClick={() => {
                            setShowQRCode(false)
                            setQrCodeData(null)
                            setVerificationCode('')
                          }}
                          className="w-full mt-2 text-gray-600 hover:text-gray-800 text-sm"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Config Management Section - Admin Only */}
            {isAdmin() && (
              <div className="mb-8">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-semibold text-gray-800">System Configuration</h3>
                  <button
                    onClick={() => setShowConfig(!showConfig)}
                    className="px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors"
                  >
                    {showConfig ? 'Hide' : 'Show'}
                  </button>
                </div>

              {showConfig && (
                <div className="space-y-6">
                  {/* File Upload Config */}
                  <div className="p-6 bg-gray-50 border border-gray-200 rounded-lg">
                    <h4 className="text-lg font-semibold text-gray-800 mb-4">File Upload Configuration</h4>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Max File Size (MB)
                        </label>
                        <input
                          type="number"
                          value={(config.file_upload.max_size / (1024 * 1024)).toFixed(2)}
                          onChange={(e) => setConfig({
                            ...config,
                            file_upload: { ...config.file_upload, max_size: Math.round(parseFloat(e.target.value) * 1024 * 1024) }
                          })}
                          min="0.1"
                          max="100"
                          step="0.1"
                          className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100"
                        />
                        <p className="text-xs text-gray-500 mt-1">Max size: 100 MB</p>
                      </div>
                      {configError && (
                        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm">
                          {configError}
                        </div>
                      )}
                      <button
                        onClick={updateFileUploadConfig}
                        disabled={configLoading}
                        className="w-full bg-emerald-500 text-white py-3 rounded-lg font-semibold hover:bg-emerald-600 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
                      >
                        {configLoading ? (
                          <div className="flex items-center justify-center">
                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                            <span className="ml-2">Updating...</span>
                          </div>
                        ) : 'Update File Upload Config'}
                      </button>
                    </div>
                  </div>

                  {/* Allowed Users Config */}
                  <div className="p-6 bg-gray-50 border border-gray-200 rounded-lg">
                    <h4 className="text-lg font-semibold text-gray-800 mb-4">Allowed Users</h4>
                    <div className="space-y-4">
                      {/* Add new user input */}
                      <div className="flex gap-2">
                        <input
                          type="text"
                          value={newUserEmail}
                          onChange={(e) => setNewUserEmail(e.target.value)}
                          onKeyDown={(e) => e.key === 'Enter' && addUser()}
                          placeholder="Enter email or username"
                          className="flex-1 px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100"
                        />
                        <button
                          onClick={addUser}
                          className="px-6 py-3 bg-emerald-500 text-white rounded-lg font-semibold hover:bg-emerald-600 transition-colors"
                        >
                          Add
                        </button>
                      </div>

                      {/* User cards */}
                      <div className="flex flex-wrap gap-2">
                        {config.allowed_users.map((email) => (
                          <div
                            key={email}
                            className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-lg shadow-sm"
                          >
                            <span className="text-sm text-gray-700">{email}</span>
                            <button
                              onClick={() => removeUser(email)}
                              className="text-gray-400 hover:text-red-500 transition-colors"
                              title="Remove user"
                            >
                              <svg
                                xmlns="http://www.w3.org/2000/svg"
                                className="h-4 w-4"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                              >
                                <path
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeWidth={2}
                                  d="M6 18L18 6M6 6l12 12"
                                />
                              </svg>
                            </button>
                          </div>
                        ))}
                        {config.allowed_users.length === 0 && (
                          <p className="text-sm text-gray-500 italic">No users added yet</p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
            )}
          </div>
        </div>
      </div>
    </div>
    </>
  )
}

export default Settings
