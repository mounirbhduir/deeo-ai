/**
 * PublicationModal Component (Phase 4 - Step 5)
 *
 * Modal displaying detailed information about a publication.
 *
 * PHASE A: Added safe data handling for citations and author names
 */

import { Modal } from '../common/Modal'
import { Badge } from '../common/Badge'
import { Button } from '../common/Button'
import { ExternalLink } from '../common/ExternalLink'
import type { PublicationDetailed } from '@/types/publication'
import { displayCitations, safePublicationAuteur } from '@/utils/dataHelpers'

interface PublicationModalProps {
  publication: PublicationDetailed | null
  isOpen: boolean
  onClose: () => void
}

export const PublicationModal = ({
  publication,
  isOpen,
  onClose,
}: PublicationModalProps) => {
  if (!publication) return null

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }

  const formatAuthorName = (author: any) => {
    const safe = safePublicationAuteur(author)
    return safe.prenom ? `${safe.prenom} ${safe.nom}` : safe.nom
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={publication.titre}>
      <div className="space-y-4">
        {/* Metadata */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="font-medium text-gray-700">Type:</span>
            <Badge variant="info" className="ml-2">
              {publication.type_publication}
            </Badge>
          </div>
          <div>
            <span className="font-medium text-gray-700">Date:</span>
            <span className="ml-2 text-gray-600">
              {formatDate(publication.date_publication)}
            </span>
          </div>
          <div>
            <span className="font-medium text-gray-700">Citations:</span>
            <span className="ml-2 text-gray-600">
              {displayCitations(publication.nombre_citations)}
            </span>
          </div>
        </div>

        {/* External Resources */}
        {(publication.doi || publication.arxiv_id) && (
          <div className="bg-gray-50 p-4 rounded-lg space-y-2">
            <h4 className="text-sm font-semibold text-gray-700 mb-3">External Resources</h4>

            {publication.doi && (
              <ExternalLink
                href={`https://doi.org/${publication.doi}`}
                label="DOI"
                value={publication.doi}
              />
            )}

            {publication.arxiv_id && (
              <ExternalLink
                href={`https://arxiv.org/abs/${publication.arxiv_id}`}
                label="arXiv"
                value={publication.arxiv_id}
              />
            )}
          </div>
        )}

        {/* Authors */}
        <div>
          <h4 className="font-medium text-gray-700 mb-2">Auteurs</h4>
          <div className="flex flex-wrap gap-2">
            {publication.auteurs.map((auteur) => (
              <Badge key={auteur.id} variant="default">
                {formatAuthorName(auteur)}
              </Badge>
            ))}
          </div>
        </div>

        {/* Organizations */}
        {publication.organisations.length > 0 && (
          <div>
            <h4 className="font-medium text-gray-700 mb-2">Organisations</h4>
            <div className="flex flex-wrap gap-2">
              {publication.organisations.map((org) => (
                <Badge key={org.id} variant="success">
                  {org.nom}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Themes */}
        <div>
          <h4 className="font-medium text-gray-700 mb-2">Thèmes</h4>
          <div className="flex flex-wrap gap-2">
            {publication.themes.map((theme) => (
              <Badge key={theme.id} variant="primary">
                {theme.label}
              </Badge>
            ))}
          </div>
        </div>

        {/* Abstract */}
        <div>
          <h4 className="font-medium text-gray-700 mb-2">Résumé</h4>
          <p className="text-sm text-gray-600 leading-relaxed whitespace-pre-line">
            {publication.abstract}
          </p>
        </div>

      </div>
    </Modal>
  )
}
