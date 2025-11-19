/**
 * PublicationModal Component (Phase 4 - Step 5)
 *
 * Modal displaying detailed information about a publication.
 */

import { Modal } from '../common/Modal'
import { Badge } from '../common/Badge'
import { Button } from '../common/Button'
import type { PublicationDetailed } from '@/types/publication'

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
              {publication.nombre_citations}
            </span>
          </div>
          {publication.doi && (
            <div>
              <span className="font-medium text-gray-700">DOI:</span>
              <a
                href={`https://doi.org/${publication.doi}`}
                target="_blank"
                rel="noopener noreferrer"
                className="ml-2 text-indigo-600 hover:underline"
              >
                {publication.doi}
              </a>
            </div>
          )}
        </div>

        {/* Authors */}
        <div>
          <h4 className="font-medium text-gray-700 mb-2">Auteurs</h4>
          <div className="flex flex-wrap gap-2">
            {publication.auteurs.map((auteur) => (
              <Badge key={auteur.id} variant="default">
                {auteur.prenom} {auteur.nom}
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

        {/* Actions */}
        <div className="flex gap-2 pt-4 border-t border-gray-200">
          {publication.arxiv_id && (
            <Button
              variant="primary"
              onClick={() =>
                window.open(
                  `https://arxiv.org/abs/${publication.arxiv_id}`,
                  '_blank'
                )
              }
            >
              Voir sur arXiv
            </Button>
          )}
          {publication.doi && (
            <Button
              variant="secondary"
              onClick={() =>
                window.open(`https://doi.org/${publication.doi}`, '_blank')
              }
            >
              Voir DOI
            </Button>
          )}
        </div>
      </div>
    </Modal>
  )
}
