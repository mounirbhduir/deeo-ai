/**
 * PublicationCard Component (Phase 4 - Step 5)
 *
 * Display card for a single publication in search results.
 *
 * PHASE A: Added safe data handling for citations and author names
 */

import { Link } from 'react-router-dom'
import { Card } from '../common/Card'
import { Badge } from '../common/Badge'
import { Button } from '../common/Button'
import type { PublicationDetailed } from '@/types/publication'
import { displayCitations, safePublicationAuteur } from '@/utils/dataHelpers'

interface PublicationCardProps {
  publication: PublicationDetailed
  onViewDetails: (id: string) => void
}

export const PublicationCard = ({
  publication,
  onViewDetails,
}: PublicationCardProps) => {
  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }

  // DEFENSIVE: Handle undefined/null text
  const truncate = (text: string | undefined | null, length: number) => {
    const safeText = text || ''
    return safeText.length > length ? safeText.substring(0, length) + '...' : safeText
  }

  const formatAuthorName = (author: any) => {
    const safe = safePublicationAuteur(author)
    return safe.prenom ? `${safe.prenom} ${safe.nom}` : safe.nom
  }

  return (
    <Card variant="bordered" className="hover:shadow-md transition-shadow">
      <div className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between mb-2">
          <h3 className="text-lg font-semibold text-gray-900 flex-1 pr-4">
            {publication.titre}
          </h3>
          <Badge variant="info">{publication.type_publication}</Badge>
        </div>

        {/* Authors - Clickable links */}
        {/* DEFENSIVE: Handle undefined auteurs array */}
        <div className="text-sm text-gray-600 mb-2">
          {(publication.auteurs || []).slice(0, 3).map((author, idx) => (
            <span key={author.id}>
              {idx > 0 && ', '}
              <Link
                to={`/authors/${author.id}`}
                className="text-indigo-600 hover:text-indigo-800 hover:underline"
                onClick={(e) => e.stopPropagation()}
              >
                {formatAuthorName(author)}
              </Link>
            </span>
          ))}
          {(publication.auteurs || []).length > 3 && (
            <span className="text-gray-500">
              {' '}et {(publication.auteurs || []).length - 3} autres
            </span>
          )}
        </div>

        {/* Abstract */}
        {/* DEFENSIVE: Handle undefined abstract */}
        {publication.abstract && (
          <p className="text-sm text-gray-700 mb-3">
            {truncate(publication.abstract, 200)}
          </p>
        )}

        {/* Metadata */}
        <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
          <span>📅 {formatDate(publication.date_publication)}</span>
          <span>📚 {displayCitations(publication.nombre_citations)} citations</span>
          {publication.doi && <span>🔗 DOI</span>}
        </div>

        {/* Themes */}
        {/* DEFENSIVE: Handle undefined themes array */}
        {(publication.themes || []).length > 0 && (
          <div className="flex flex-wrap gap-2 mb-3">
            {(publication.themes || []).slice(0, 3).map((theme) => (
              <Badge key={theme.id} variant="default" size="sm">
                {theme.label}
              </Badge>
            ))}
            {(publication.themes || []).length > 3 && (
              <Badge variant="default" size="sm">
                +{(publication.themes || []).length - 3}
              </Badge>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center gap-2">
          <Button
            variant="primary"
            size="sm"
            onClick={() => onViewDetails(publication.id)}
          >
            Voir détails
          </Button>
          {publication.arxiv_id && (
            <Button
              variant="secondary"
              size="sm"
              onClick={() =>
                window.open(
                  `https://arxiv.org/abs/${publication.arxiv_id}`,
                  '_blank'
                )
              }
            >
              arXiv
            </Button>
          )}
        </div>
      </div>
    </Card>
  )
}
