import { ExternalLink, MapPin, Globe, Building2 } from 'lucide-react'
import { Badge } from '@/components/common/Badge'
import type { OrganisationProfile } from '@/types/organisation'

const TYPE_COLORS = {
  academic: 'primary',
  industry: 'info',
  research_center: 'success',
  think_tank: 'warning',
} as const

export const OrganisationHeader = ({ organisation }: { organisation: OrganisationProfile }) => {
  return (
    <div className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row gap-6 items-start">
          <div className="flex-shrink-0 w-24 h-24 bg-indigo-100 rounded-lg flex items-center justify-center">
            <Building2 className="w-12 h-12 text-indigo-600" />
          </div>
          <div className="flex-1 min-w-0">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{organisation.nom}</h1>
            {organisation.nom_court && (
              <p className="text-lg text-gray-500 mb-3">{organisation.nom_court}</p>
            )}
            <div className="flex flex-wrap gap-2 mb-4">
              <Badge variant={TYPE_COLORS[organisation.type]}>{organisation.type.replace('_', ' ')}</Badge>
              {organisation.ranking_mondial && (
                <Badge variant="info">World Ranking #{organisation.ranking_mondial}</Badge>
              )}
            </div>
            <div className="flex flex-col gap-2 text-gray-600">
              <div className="flex items-center gap-2">
                <MapPin className="w-4 h-4" />
                <span>{organisation.ville}, {organisation.pays}</span>
                {organisation.secteur && <span className="text-gray-400">• {organisation.secteur}</span>}
              </div>
              {organisation.url && (
                <div className="flex items-center gap-2">
                  <Globe className="w-4 h-4" />
                  <a href={organisation.url} target="_blank" rel="noopener noreferrer" className="hover:text-indigo-600 transition-colors inline-flex items-center gap-1">
                    {organisation.url.replace(/^https?:\/\//, '')}
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
