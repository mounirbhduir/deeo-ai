import { Users, BookOpen, Quote, Award } from 'lucide-react'
import { Card } from '@/components/common/Card'
import type { OrganisationProfile } from '@/types/organisation'

interface OrganisationStatsProps {
  organisation: OrganisationProfile
}

export const OrganisationStats = ({ organisation }: OrganisationStatsProps) => {
  const stats = [
    {
      label: 'Researchers',
      value: organisation.nombre_chercheurs,
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      label: 'Publications',
      value: organisation.nombre_publications,
      icon: BookOpen,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      label: 'Citations',
      value: organisation.total_citations?.toLocaleString() || 0,
      icon: Quote,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      label: 'World Ranking',
      value: organisation.ranking_mondial ? `#${organisation.ranking_mondial}` : 'N/A',
      icon: Award,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
    },
  ]

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat) => {
        const Icon = stat.icon
        return (
          <Card key={stat.label} className="p-6">
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                <Icon className={`w-6 h-6 ${stat.color}`} />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
                <div className="text-sm text-gray-500">{stat.label}</div>
              </div>
            </div>
          </Card>
        )
      })}
    </div>
  )
}
