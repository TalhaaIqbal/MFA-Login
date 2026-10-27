import { Helmet } from 'react-helmet-async'
import { useNavigate } from 'react-router-dom'

function NotFound() {
  const navigate = useNavigate()

  return (
    <>
      <Helmet>
        <title>404 - Page Not Found | Scraper Dashboard</title>
        <meta name="description" content="The page you are looking for does not exist. Return to the Scraper Dashboard." />
      </Helmet>

      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-800 to-gray-600 p-4">
        <div className="bg-white rounded-xl p-10 w-full max-w-md shadow-2xl text-center">
          <div className="text-6xl font-bold text-emerald-500 mb-4">404</div>
          <h1 className="text-3xl font-semibold text-gray-800 mb-2">Page Not Found</h1>
          <p className="text-gray-500 text-sm mb-8">
            The page you are looking for does not exist or has been moved.
          </p>
          <button
            onClick={() => navigate('/dashboard')}
            className="w-full bg-emerald-500 text-white py-3 rounded-lg font-semibold hover:bg-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-300 transition-all"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    </>
  )
}

export default NotFound
