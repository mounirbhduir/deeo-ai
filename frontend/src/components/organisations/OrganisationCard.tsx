import { Link } from 'react-router-dom'
import { Building2, Users, BookOpen, Quote, MapPin } from 'lucide-react'
import { Card } from '@/components/common/Card'
import { Badge } from '@/components/common/Badge'
import type { OrganisationListItem } from '@/types/organisation'

interface OrganisationCardProps {
  organisation: OrganisationListItem
}

const TYPE_COLORS = {
  academic: 'primary',
  industry: 'info',
  research_center: 'success',
  think_tank: 'warning',
} as const

export const OrganisationCard = ({ organisation }: OrganisationCardProps) => {
  return (
    <Link to={`/organisations/${organisation.id}`}>
      <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
        <div className="flex flex-col gap-4">
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0 w-16 h-16 bg-indigo-100 rounded-lg flex items-center justify-center">
              <Building2 className="w-8 h-8 text-indigo-600" />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-lg font-semibold text-gray-900 truncate">{organisation.nom}</h3>
              {organisation.nom_court && (
                <p className="text-sm text-gray-500">{organisation.nom_court}</p>
              )}
              <div className="flex items-center gap-2 mt-1">
                <Badge variant={TYPE_COLORS[organisation.type]} size="sm">{organisation.type}</Badge>
                <div className="flex items-center text-xs text-gray-500">
                  <MapPin className="w-3 h-3 mr-1" />
                  {organisation.ville}, {organisation.pays}
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div className="flex flex-col items-center p-2 bg-gray-50 rounded-lg">
              <Users className="w-4 h-4 text-gray-500 mb-1" />
              <div className="text-xl font-bold text-gray-900">{organisation.nombre_chercheurs}</div>
              <div className="text-xs text-gray-500">Researchers</div>
            </div>
            <div className="flex flex-col items-center p-2 bg-gray-50 rounded-lg">
              <BookOpen className="w-4 h-4 text-gray-500 mb-1" />
              <div className="text-xl font-bold text-gray-900">{organisation.nombre_publications}</div>
              <div className="text-xs text-gray-500">Papers</div>
            </div>
            <div className="flex flex-col items-center p-2 bg-gray-50 rounded-lg">
              <Quote className="w-4 h-4 text-gray-500 mb-1" />
              <div className="text-xl font-bold text-gray-900">{organisation.total_citations?.toLocaleString() || 0}</div>
              <div className="text-xs text-gray-500">Citations</div>
            </div>
          </div>

          {organisation.ranking_mondial && (
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-500">World Ranking</span>
              <Badge variant="info" size="sm">#{organisation.ranking_mondial}</Badge>
            </div>
          )}
        </div>
      </Card>
    </Link>
  )
}
