import { useAuth } from '../context/AuthContext'
import Sidebar from '../components/sidebar/Sidebar'
import TopNav from '../components/TopNav'
import { Helmet } from 'react-helmet-async'
import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import api from '../utils/api'
import logger from '../utils/logger'

function Dashboard() {
  const { user, isAdmin } = useAuth()
  const [dbHealth, setDbHealth] = useState(null)
  const [healthHistory, setHealthHistory] = useState([])
  const [loading, setLoading] = useState(true)

  const canViewHealth = isAdmin()

  const fetchHealth = useCallback(async () => {
    try {
      const response = await api.get('/health/db')
      const healthData = response.data.data

      setDbHealth(healthData)

      // Add to history (keep last 20 data points)
      setHealthHistory(prev => {
        const newHistory = [
          ...prev,
          {
            timestamp: new Date(healthData.last_check),
            latency: healthData.latency_ms,
            status: healthData.status
          }
        ]
        return newHistory.slice(-20)
      })

      setLoading(false)
    } catch (error) {
      logger.error('Error fetching health:', error)
      if (!dbHealth) {
        setDbHealth({
          status: 'unhealthy',
          latency_ms: null,
          last_check: new Date().toISOString(),
          error: 'Failed to fetch health status'
        })
      }
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (canViewHealth) {
      fetchHealth()
      const interval = setInterval(fetchHealth, 30000) // Poll every 30 seconds
      return () => clearInterval(interval)
    }
  }, [canViewHealth, fetchHealth])

  const getStatusColor = (status) => {
    return status === 'healthy' ? 'bg-green-500' : 'bg-red-500'
  }

  const getStatusTextColor = (status) => {
    return status === 'healthy' ? 'text-green-600' : 'text-red-600'
  }

  return (
    <>
      <Helmet>
        <title>Dashboard | Scraper Dashboard</title>
        <meta name="description" content="View your scraper dashboard overview and manage your web scraping applications." />
      </Helmet>

      <div className="flex min-h-screen bg-gradient-to-br from-gray-800 to-gray-600">
      <Sidebar />

      <div className="flex-1 flex flex-col">
        <TopNav title="Dashboard" />

        <div className="flex-1 p-8">
          <div className="space-y-6">
            {/* Database Health Card - Admin Only */}
            {canViewHealth && (
              <div className="bg-white rounded-xl shadow-2xl p-8">
                <h2 className="text-3xl font-semibold text-gray-800 mb-6">Database Health</h2>

                {loading ? (
                  <div className="flex items-center justify-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500"></div>
                    <span className="ml-4 text-gray-600">Loading health status...</span>
                  </div>
                ) : dbHealth ? (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-4">
                        <div className={`w-4 h-4 rounded-full ${getStatusColor(dbHealth.status)}`}></div>
                        <div>
                          <p className="text-lg font-semibold text-gray-800">
                            Status: <span className={getStatusTextColor(dbHealth.status)}>{dbHealth.status.toUpperCase()}</span>
                          </p>
                          <p className="text-sm text-gray-500">Database: {dbHealth.database}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-semibold text-gray-800">
                          {dbHealth.latency_ms !== null ? `${dbHealth.latency_ms} ms` : 'N/A'}
                        </p>
                        <p className="text-sm text-gray-500">Latency</p>
                      </div>
                    </div>

                    <div className="p-4 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-600">
                        <strong>Last Check:</strong> {new Date(dbHealth.last_check).toLocaleString()}
                      </p>
                    </div>

                    {/* Enhanced Health Graph */}
                    {healthHistory.length > 0 && (
                      <div className="mt-6">
                        <h3 className="text-lg font-semibold text-gray-800 mb-4">Latency History (Last 20 checks)</h3>
                        <div className="h-64 bg-gray-50 rounded-lg p-4 relative border border-gray-200">
                          <svg className="w-full h-full" viewBox="0 0 400 160">
                            {/* Grid lines */}
                            {[0, 0.25, 0.5, 0.75, 1].map((percent) => (
                              <line
                                key={percent}
                                x1="40"
                                y1={20 + percent * 120}
                                x2="390"
                                y2={20 + percent * 120}
                                stroke="#e5e7eb"
                                strokeWidth="1"
                                strokeDasharray="4"
                              />
                            ))}

                            {/* Y-axis labels */}
                            {healthHistory.length > 0 && (() => {
                              const maxLatency = Math.max(...healthHistory.map(h => h.latency || 0), 100)
                              return [0, 0.25, 0.5, 0.75, 1].map((percent) => (
                                <text
                                  key={percent}
                                  x="35"
                                  y={24 + percent * 120}
                                  textAnchor="end"
                                  className="text-xs fill-gray-500"
                                >
                                  {Math.round(maxLatency * (1 - percent))}
                                </text>
                              ))
                            })()}

                            {/* X-axis label */}
                            <text x="215" y="155" textAnchor="middle" className="text-xs fill-gray-500">
                              Time (Last 20 checks)
                            </text>

                            {/* Y-axis label */}
                            <text x="8" y="80" textAnchor="middle" transform="rotate(-90, 8, 80)" className="text-xs fill-gray-500">
                              Latency (ms)
                            </text>

                            {/* Data line */}
                            {healthHistory.length > 1 && (
                              <polyline
                                points={healthHistory.map((point, index) => {
                                  const x = 40 + (index / (healthHistory.length - 1)) * 350
                                  const maxLatency = Math.max(...healthHistory.map(h => h.latency || 0), 100)
                                  const y = 140 - ((point.latency || 0) / maxLatency) * 120
                                  return `${x},${y}`
                                }).join(' ')}
                                fill="none"
                                stroke={dbHealth.status === 'healthy' ? '#10b981' : '#ef4444'}
                                strokeWidth="2"
                              />
                            )}

                            {/* Data points */}
                            {healthHistory.map((point, index) => {
                              const x = 40 + (index / (healthHistory.length - 1 || 1)) * 350
                              const maxLatency = Math.max(...healthHistory.map(h => h.latency || 0), 100)
                              const y = 140 - ((point.latency || 0) / maxLatency) * 120
                              return (
                                <g key={index}>
                                  <circle
                                    cx={x}
                                    cy={y}
                                    r={5}
                                    fill={point.status === 'healthy' ? '#10b981' : '#ef4444'}
                                    stroke="white"
                                    strokeWidth="2"
                                  />
                                  {/* Tooltip */}
                                  <title>
                                    Check {index + 1}: {point.latency}ms - {point.status}
                                  </title>
                                </g>
                              )
                            })}
                          </svg>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-red-800">Failed to load health status</p>
                  </div>
                )}
              </div>
            )}

            {/* User Info Card */}
            <div className="bg-white rounded-xl shadow-2xl p-8">
              <h2 className="text-3xl font-semibold text-gray-800 mb-6">User Information</h2>
              <div className="space-y-4">
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-gray-600"><strong>User ID:</strong> {user?.id}</p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-gray-600"><strong>Email:</strong> {user?.email}</p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <p className="text-gray-600"><strong>Role:</strong> {user?.role}</p>
                </div>
                <div className="p-4 bg-gray-50 rounded-lg">
                  <Link to="/privacy-policy" className="text-emerald-600 hover:text-emerald-700">
                    View Privacy Policy
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    </>
  )
}

export default Dashboard
