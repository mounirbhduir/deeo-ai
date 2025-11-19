/**
 * AuthorPublications Component (Phase 4 - Step 6)
 *
 * Displays author's publications with filtering, sorting, and pagination.
 * Reuses PublicationCard from Step 5 for consistent display.
 */

import { useState } from 'react'
import { useAuthorPublications } from '@/hooks/useAuthorPublications'
import { PublicationCard } from '@/components/search/PublicationCard'
import { PublicationModal } from '@/components/search/PublicationModal'
import { Pagination } from '@/components/common/Pagination'
import { Loader } from '@/components/common/Loader'
import { Alert } from '@/components/common/Alert'
import { BookOpen } from 'lucide-react'
import { publicationsApi } from '@/api/publications'
import type { PublicationDetailed } from '@/types/publication'

interface AuthorPublicationsProps {
  authorId: string
}

export const AuthorPublications = ({ authorId }: AuthorPublicationsProps) => {
  const { data, isLoading, isError, error, queryParams, updateParams } =
    useAuthorPublications(authorId)

  const [selectedPublication, setSelectedPublication] =
    useState<PublicationDetailed | null>(null)
  const [modalOpen, setModalOpen] = useState(false)

  // Extract unique years, types, themes from data for filters
  const availableYears = data?.items
    ? Array.from(
        new Set(
          data.items.map((p) =>
            new Date(p.date_publication).getFullYear().toString()
          )
        )
      ).sort((a, b) => parseInt(b) - parseInt(a))
    : []

  const availableTypes = data?.items
    ? Array.from(new Set(data.items.map((p) => p.type_publication)))
    : []

  const availableThemes = data?.items
    ? Array.from(
        new Set(data.items.flatMap((p) => p.themes.map((t) => t.label)))
      )
    : []

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Loader size="lg" />
      </div>
    )
  }

  if (isError) {
    return (
      <Alert variant="error">
        Error loading publications: {error?.message || 'Unknown error'}
      </Alert>
    )
  }

  if (!data || data.items.length === 0) {
    return (
      <div className="text-center py-12">
        <BookOpen className="w-16 h-16 mx-auto text-gray-300 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          No publications found
        </h3>
        <p className="text-gray-500">
          {queryParams.year || queryParams.type || queryParams.theme
            ? 'Try adjusting your filters'
            : 'This author has no publications yet'}
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Year Filter */}
          <select
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            value={queryParams.year?.toString() || ''}
            onChange={(e) =>
              updateParams({
                year: e.target.value ? parseInt(e.target.value) : undefined,
                page: 1,
              })
            }
          >
            <option value="">All Years</option>
            {availableYears.map((year) => (
              <option key={year} value={year}>
                {year}
              </option>
            ))}
          </select>

          {/* Type Filter */}
          <select
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            value={queryParams.type || ''}
            onChange={(e) =>
              updateParams({ type: e.target.value || undefined, page: 1 })
            }
          >
            <option value="">All Types</option>
            {availableTypes.map((type) => (
              <option key={type} value={type}>
                {type.replace('_', ' ')}
              </option>
            ))}
          </select>

          {/* Theme Filter */}
          <select
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            value={queryParams.theme || ''}
            onChange={(e) =>
              updateParams({ theme: e.target.value || undefined, page: 1 })
            }
          >
            <option value="">All Themes</option>
            {availableThemes.map((theme) => (
              <option key={theme} value={theme}>
                {theme}
              </option>
            ))}
          </select>

          {/* Sort By */}
          <select
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            value={queryParams.sort_by || 'date'}
            onChange={(e) =>
              updateParams({
                sort_by: e.target.value as 'date' | 'citations' | 'titre',
              })
            }
          >
            <option value="date">Sort by Date</option>
            <option value="citations">Sort by Citations</option>
            <option value="titre">Sort by Title</option>
          </select>
        </div>
      </div>

      {/* Results Count */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-600">
          Showing {data.items.length} of {data.total} publications
        </p>
        <select
          className="w-24 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          value={queryParams.limit?.toString() || '20'}
          onChange={(e) =>
            updateParams({ limit: parseInt(e.target.value), page: 1 })
          }
        >
          <option value="10">10</option>
          <option value="20">20</option>
          <option value="50">50</option>
        </select>
      </div>

      {/* Publications List */}
      <div className="space-y-4">
        {data.items.map((publication) => (
          <PublicationCard
            key={publication.id}
            publication={publication}
            onViewDetails={async () => {
              try {
                const fullPublication = await publicationsApi.getById(publication.id)
                setSelectedPublication(fullPublication)
                setModalOpen(true)
              } catch (err) {
                console.error('Error loading publication details:', err)
              }
            }}
          />
        ))}
      </div>

      {/* Pagination */}
      {data.total_pages > 1 && (
        <div className="flex justify-center">
          <Pagination
            currentPage={queryParams.page || 1}
            totalPages={data.total_pages}
            onPageChange={(page) => updateParams({ page })}
          />
        </div>
      )}

      {/* Publication Details Modal */}
      <PublicationModal
        publication={selectedPublication}
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false)
          setSelectedPublication(null)
        }}
      />
    </div>
  )
}
