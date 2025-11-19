/**
 * PublicationCard Component (Phase 4 - Step 5)
 *
 * Display card for a single publication in search results.
 */

import { Card } from '../common/Card'
import { Badge } from '../common/Badge'
import { Button } from '../common/Button'
import type { PublicationDetailed } from '@/types/publication'

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

  const truncate = (text: string, length: number) => {
    return text.length > length ? text.substring(0, length) + '...' : text
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

        {/* Authors */}
        <p className="text-sm text-gray-600 mb-2">
          {publication.auteurs
            .slice(0, 3)
            .map((a) => `${a.prenom} ${a.nom}`)
            .join(', ')}
          {publication.auteurs.length > 3 &&
            ` et ${publication.auteurs.length - 3} autres`}
        </p>

        {/* Abstract */}
        <p className="text-sm text-gray-700 mb-3">
          {truncate(publication.abstract, 200)}
        </p>

        {/* Metadata */}
        <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
          <span>📅 {formatDate(publication.date_publication)}</span>
          <span>📚 {publication.nombre_citations} citations</span>
          {publication.doi && <span>🔗 DOI</span>}
        </div>

        {/* Themes */}
        <div className="flex flex-wrap gap-2 mb-3">
          {publication.themes.slice(0, 3).map((theme) => (
            <Badge key={theme.id} variant="default" size="sm">
              {theme.label}
            </Badge>
          ))}
          {publication.themes.length > 3 && (
            <Badge variant="default" size="sm">
              +{publication.themes.length - 3}
            </Badge>
          )}
        </div>

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
