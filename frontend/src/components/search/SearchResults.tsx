/**
 * SearchResults Component (Phase 4 - Step 5)
 *
 * Display search results with loading, error, and empty states.
 */

import { PublicationCard } from './PublicationCard'
import { Loader } from '../common/Loader'
import { Alert } from '../common/Alert'
import type { PublicationDetailed } from '@/types/publication'

interface SearchResultsProps {
  publications: PublicationDetailed[]
  loading: boolean
  error: Error | null
  total: number
  onViewDetails: (id: string) => void
}

export const SearchResults = ({
  publications,
  loading,
  error,
  total,
  onViewDetails,
}: SearchResultsProps) => {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader size="lg" />
      </div>
    )
  }

  if (error) {
    return (
      <Alert variant="error" title="Erreur de chargement">
        {error.message || 'Une erreur est survenue lors du chargement des publications.'}
      </Alert>
    )
  }

  if (publications.length === 0) {
    return (
      <Alert variant="info" title="Aucun résultat">
        Aucune publication ne correspond à vos critères de recherche.
      </Alert>
    )
  }

  return (
    <div>
      <div className="mb-4 text-sm text-gray-600">
        {total} publication{total > 1 ? 's' : ''} trouvée{total > 1 ? 's' : ''}
      </div>
      <div className="space-y-4">
        {publications.map((publication) => (
          <PublicationCard
            key={publication.id}
            publication={publication}
            onViewDetails={onViewDetails}
          />
        ))}
      </div>
    </div>
  )
}
