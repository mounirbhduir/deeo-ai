import { Link, useLocation } from 'react-router-dom'
import { ChevronRight, Home } from 'lucide-react'

const routeLabels: Record<string, string> = {
  dashboard: 'Dashboard',
  publications: 'Publications',
  search: 'Recherche',
  auteurs: 'Auteurs',
  organisations: 'Organisations',
  themes: 'Thèmes',
}

export function Breadcrumb() {
  const location = useLocation()
  const pathSegments = location.pathname.split('/').filter(Boolean)

  if (pathSegments.length === 0) {
    return null
  }

  return (
    <nav className="flex items-center space-x-2 text-sm text-gray-600 mb-6">
      <Link to="/" className="hover:text-primary-600 flex items-center">
        <Home className="h-4 w-4" />
      </Link>

      {pathSegments.map((segment, index) => {
        const path = `/${pathSegments.slice(0, index + 1).join('/')}`
        const label = routeLabels[segment] || segment
        const isLast = index === pathSegments.length - 1

        return (
          <div key={path} className="flex items-center space-x-2">
            <ChevronRight className="h-4 w-4 text-gray-400" />
            {isLast ? (
              <span className="font-medium text-gray-900 capitalize">
                {label}
              </span>
            ) : (
              <Link to={path} className="hover:text-primary-600 capitalize">
                {label}
              </Link>
            )}
          </div>
        )
      })}
    </nav>
  )
}
