/**
 * AuthorHeader Component (Phase 4 - Step 6)
 *
 * PHASE A: Added safe data handling for affiliations
 */

import { ExternalLink, Mail, Globe } from 'lucide-react'
import { Avatar } from '@/components/common/Avatar'
import { Badge } from '@/components/common/Badge'
import { getInitials } from '@/utils/stringUtils'
import type { AuthorProfile } from '@/types/author'
import { hasData } from '@/utils/dataHelpers'

interface AuthorHeaderProps {
  author: AuthorProfile
}

export const AuthorHeader = ({ author }: AuthorHeaderProps) => {
  const fullName = `${author.prenom} ${author.nom}`
  const currentAffiliations = hasData(author.affiliations)
    ? author.affiliations.filter((aff) => !aff.date_fin)
    : []

  return (
    <div className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row gap-6 items-start">
          <Avatar alt={fullName} fallback={getInitials(fullName)} size="xl" className="flex-shrink-0" />
          <div className="flex-1 min-w-0">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{fullName}</h1>
            {currentAffiliations.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-4">
                {currentAffiliations.map((aff, idx) => (
                  <Badge key={idx} variant={aff.organisation.type === 'academic' ? 'primary' : aff.organisation.type === 'industry' ? 'info' : 'default'}>
                    {aff.poste || 'Researcher'} @ {aff.organisation.nom}
                  </Badge>
                ))}
              </div>
            )}
            {author.email && (
              <div className="flex items-center gap-2 text-gray-600 mb-2">
                <Mail className="w-4 h-4" />
                <a href={`mailto:${author.email}`} className="hover:text-indigo-600 transition-colors">{author.email}</a>
              </div>
            )}
            <div className="flex flex-wrap gap-2 mt-4">
              {author.orcid && (
                <a href={`https://orcid.org/${author.orcid}`} target="_blank" rel="noopener noreferrer" className="inline-flex items-center px-3 py-1.5 text-sm border border-gray-300 rounded-md hover:bg-gray-50">
                  <ExternalLink className="w-4 h-4 mr-1" />ORCID
                </a>
              )}
              {author.google_scholar_id && (
                <a href={`https://scholar.google.com/citations?user=${author.google_scholar_id}`} target="_blank" rel="noopener noreferrer" className="inline-flex items-center px-3 py-1.5 text-sm border border-gray-300 rounded-md hover:bg-gray-50">
                  <ExternalLink className="w-4 h-4 mr-1" />Google Scholar
                </a>
              )}
              {author.homepage_url && (
                <a href={author.homepage_url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center px-3 py-1.5 text-sm border border-gray-300 rounded-md hover:bg-gray-50">
                  <Globe className="w-4 h-4 mr-1" />Homepage
                </a>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
