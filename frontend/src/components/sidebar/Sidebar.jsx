import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'

const sidebarItems = [
  { id: 'dashboard', label: 'Dashboard', path: '/dashboard', icon: '📊' },
  { id: 'settings', label: 'Settings', path: '/settings', icon: '⚙️' },
]

function Sidebar() {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()

  const handleNavigation = (path) => {
    navigate(path)
  }

  return (
    <div className={`bg-gray-900 text-white transition-all duration-300 ${isCollapsed ? 'w-20' : 'w-64'} min-h-screen flex flex-col`}>
      <div className="p-4 border-b border-gray-700">
        <h1 className={`font-bold text-xl ${isCollapsed ? 'text-center' : ''}`}>
          {isCollapsed ? '🚀' : 'Scraper Dashboard'}
        </h1>
      </div>

      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {sidebarItems.map((item) => (
            <li key={item.id}>
              <button
                onClick={() => handleNavigation(item.path)}
                className={`w-full flex items-center p-3 rounded-lg transition-colors ${
                  location.pathname === item.path
                    ? 'bg-emerald-600 text-white'
                    : 'hover:bg-gray-800 text-gray-300'
                }`}
              >
                <span className="text-xl mr-3">{item.icon}</span>
                {!isCollapsed && <span>{item.label}</span>}
              </button>
            </li>
          ))}
        </ul>
      </nav>

      <div className="p-4 border-t border-gray-700">
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="w-full flex items-center justify-center p-2 rounded-lg hover:bg-gray-800 transition-colors"
        >
          {isCollapsed ? '→' : '←'}
        </button>
      </div>
    </div>
  )
}

export default Sidebar
