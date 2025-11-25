/**
 * AuthorCard Component (Phase 4 - Step 6)
 *
 * Compact author card for displaying in lists/grids.
 * Shows avatar, name, h-index, publications, citations, and affiliations.
 *
 * PHASE A: Added safe data handling for h-index and citations
 */

import { Link } from 'react-router-dom'
import { Award, BookOpen, Quote } from 'lucide-react'
import { Card } from '@/components/common/Card'
import { Badge } from '@/components/common/Badge'
import { Avatar } from '@/components/common/Avatar'
import { getInitials } from '@/utils/stringUtils'
import type { AuthorListItem } from '@/types/author'
import { displayHIndex, displayCitations, hasData } from '@/utils/dataHelpers'

interface AuthorCardProps {
  author: AuthorListItem
}

export const AuthorCard = ({ author }: AuthorCardProps) => {
  // DEFENSIVE: Handle potentially undefined fields
  const prenom = author?.prenom || ''
  const nom = author?.nom || 'Inconnu'
  const fullName = prenom ? `${prenom} ${nom}` : nom

  // DEFENSIVE: affiliations may not exist in list response (only in detail)
  const affiliations = author?.affiliations || []
  const currentAffiliations = affiliations.filter((aff) => aff && !aff.date_fin)

  return (
    <Link to={`/authors/${author?.id ?? ''}`}>
      <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
        <div className="flex flex-col gap-4">
          {/* Header: Avatar + Name */}
          <div className="flex items-start gap-4">
            <Avatar
              alt={fullName}
              fallback={getInitials(fullName)}
              size="lg"
              className="flex-shrink-0"
            />
            <div className="flex-1 min-w-0">
              <h3 className="text-lg font-semibold text-gray-900 truncate">
                {fullName}
              </h3>
              {currentAffiliations.length > 0 && currentAffiliations[0]?.organisation?.nom && (
                <p className="text-sm text-gray-600 truncate">
                  {currentAffiliations[0].organisation.nom}
                </p>
              )}
            </div>
          </div>

          {/* Metrics */}
          <div className="grid grid-cols-3 gap-3">
            <div className="flex flex-col items-center p-2 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-1 text-gray-500 mb-1">
                <Award className="w-4 h-4" />
              </div>
              <div className="text-lg font-bold text-gray-900">
                {displayHIndex(author?.h_index)}
              </div>
              <div className="text-xs text-gray-500">h-index</div>
            </div>

            <div className="flex flex-col items-center p-2 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-1 text-gray-500 mb-1">
                <BookOpen className="w-4 h-4" />
              </div>
              <div className="text-xl font-bold text-gray-900">
                {author?.nombre_publications ?? 0}
              </div>
              <div className="text-xs text-gray-500">Papers</div>
            </div>

            <div className="flex flex-col items-center p-2 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-1 text-gray-500 mb-1">
                <Quote className="w-4 h-4" />
              </div>
              <div className="text-lg font-bold text-gray-900">
                {displayCitations(author?.nombre_citations)}
              </div>
              <div className="text-xs text-gray-500">Citations</div>
            </div>
          </div>

          {/* Affiliations Badges - DEFENSIVE: Only show if data exists and is valid */}
          {currentAffiliations.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {currentAffiliations.slice(0, 2).map((aff, idx) => (
                aff?.organisation?.type && (
                  <Badge
                    key={idx}
                    variant={aff.organisation.type === 'academic' ? 'primary' : 'info'}
                    size="sm"
                  >
                    {aff?.poste || aff.organisation.type}
                  </Badge>
                )
              ))}
              {currentAffiliations.length > 2 && (
                <Badge variant="default" size="sm">
                  +{currentAffiliations.length - 2} more
                </Badge>
              )}
            </div>
          )}
        </div>
      </Card>
    </Link>
  )
}
