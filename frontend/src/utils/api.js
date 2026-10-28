import axios from 'axios'

const baseURL = import.meta.env.VITE_API_URI || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL,
  withCredentials: true,
})

if (baseURL.includes('ngrok')) {
  api.defaults.headers['ngrok-skip-browser-warning'] = 'true'
}

const AUTH_PATHS = ['/auth/me', '/auth/login', '/auth/signup', '/auth/logout', '/auth/2fa/verify', '/auth/email-otp/verify', '/auth/2fa/disable', '/auth/email-otp/disable', '/auth/email-otp/send-disable-code']

// Session expired mid-use: send back to login (not for the auth calls themselves)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const url = error.config?.url || ''
    if (error.response?.status === 401 && !AUTH_PATHS.some((p) => url.startsWith(p))) {
      localStorage.removeItem('user')
      if (!['/login', '/signup'].includes(window.location.pathname)) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default api
