import axios from 'axios'

// Create shared axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URI || 'http://localhost:8000/api/v1',
  headers: {},
  withCredentials: true  // Required for HttpOnly cookies
})

// Add ngrok header only if using ngrok (development convenience)
const baseURL = import.meta.env.VITE_API_URI || 'http://localhost:8000/api/v1'
if (baseURL.includes('ngrok')) {
  api.defaults.headers['ngrok-skip-browser-warning'] = 'true'
}

// Request interceptor - cookies are sent automatically with withCredentials
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Only redirect if user was previously authenticated (session expired)
      // Don't redirect for login attempts with invalid credentials
      const user = localStorage.getItem('user')
      if (user) {
        localStorage.removeItem('user')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
