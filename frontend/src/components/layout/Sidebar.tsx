import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  FileText,
  Users,
  Building2,
  Network,
  Tags,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react'

const sidebarItems = [
  { name: 'Tableau de bord', path: '/dashboard', icon: LayoutDashboard },
  { name: 'Publications', path: '/publications/search', icon: FileText },
  { name: 'Auteurs', path: '/authors', icon: Users },
  { name: 'Organisations', path: '/organisations', icon: Building2 },
  { name: 'Graphes réseau', path: '/graphs', icon: Network },
  { name: 'Thèmes', path: '/themes', icon: Tags },
]

interface SidebarProps {
  collapsed?: boolean
}

export function Sidebar({ collapsed: initialCollapsed = false }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(initialCollapsed)
  const location = useLocation()

  const isActive = (path: string) => location.pathname.startsWith(path)

  return (
    <aside
      className={`hidden lg:flex flex-col bg-gray-50 border-r border-gray-200 transition-all duration-300 ${
        collapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Collapse Toggle */}
      <div className="flex items-center justify-end p-4 border-b border-gray-200">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-2 rounded-md hover:bg-gray-200 transition-colors"
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? (
            <ChevronRight className="h-5 w-5 text-gray-600" />
          ) : (
            <ChevronLeft className="h-5 w-5 text-gray-600" />
          )}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {sidebarItems.map((item) => {
          const Icon = item.icon
          const active = isActive(item.path)

          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                active
                  ? 'bg-primary-100 text-primary-700'
                  : 'text-gray-700 hover:bg-gray-200'
              }`}
              title={collapsed ? item.name : undefined}
            >
              <Icon className="h-5 w-5 flex-shrink-0" />
              {!collapsed && <span className="ml-3">{item.name}</span>}
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
