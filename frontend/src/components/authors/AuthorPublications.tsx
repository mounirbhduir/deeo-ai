/**
 * AuthorPublications Component (Phase 4 - Step 6)
 *
 * Displays author's publications with filtering, sorting, and pagination.
 * Uses client-side filtering instead of API calls.
 * FIX: No longer makes 404 network requests - filters local data instead.
 */

import { useState, useMemo } from 'react'
import { useSearchParams } from 'react-router-dom'
import { PublicationCard } from '@/components/search/PublicationCard'
import { PublicationModal } from '@/components/search/PublicationModal'
import { Pagination } from '@/components/common/Pagination'
import { BookOpen } from 'lucide-react'
import { publicationsApi } from '@/api/publications'
import type { PublicationDetailed } from '@/types/publication'

interface AuthorPublicationsProps {
  publications: any[]  // Publications from author profile
}

export const AuthorPublications = ({ publications }: AuthorPublicationsProps) => {
  const [searchParams, setSearchParams] = useSearchParams()

  // Parse query params from URL
  const yearFilter = searchParams.get('year')
  const typeFilter = searchParams.get('type')
  const themeFilter = searchParams.get('theme')
  const sortBy = searchParams.get('sort_by') || 'date'
  const sortOrder = searchParams.get('order') || 'desc'
  const page = parseInt(searchParams.get('page') || '1', 10)
  const limit = parseInt(searchParams.get('limit') || '20', 10)

  const [selectedPublication, setSelectedPublication] =
    useState<PublicationDetailed | null>(null)
  const [modalOpen, setModalOpen] = useState(false)

  // Update search params helper
  const updateParams = (newParams: Record<string, any>) => {
    const params = new URLSearchParams(searchParams)
    Object.entries(newParams).forEach(([key, value]) => {
      if (value === undefined || value === null || value === '') {
        params.delete(key)
      } else {
        params.set(key, String(value))
      }
    })
    setSearchParams(params)
  }

  // CLIENT-SIDE FILTERING AND SORTING
  const { filteredAndSorted, totalPages } = useMemo(() => {
    if (!publications || publications.length === 0) {
      return { filteredAndSorted: [], totalPages: 0 }
    }

    // Apply filters
    let filtered = publications.filter((pub) => {
      // Year filter
      if (yearFilter) {
        const pubYear = pub.date_publication ? new Date(pub.date_publication).getFullYear() : null
        if (pubYear !== parseInt(yearFilter)) return false
      }

      // Type filter
      if (typeFilter && pub.type_publication !== typeFilter) {
        return false
      }

      // Theme filter
      if (themeFilter) {
        const hasTheme = pub.themes?.some((t: any) => t.label === themeFilter)
        if (!hasTheme) return false
      }

      return true
    })

    // Apply sorting
    filtered = [...filtered].sort((a, b) => {
      let aVal, bVal

      if (sortBy === 'date') {
        aVal = a.date_publication ? new Date(a.date_publication).getTime() : 0
        bVal = b.date_publication ? new Date(b.date_publication).getTime() : 0
      } else if (sortBy === 'citations') {
        aVal = a.nombre_citations || 0
        bVal = b.nombre_citations || 0
      } else {
        // titre
        aVal = a.titre || ''
        bVal = b.titre || ''
      }

      if (sortOrder === 'asc') {
        return aVal > bVal ? 1 : -1
      } else {
        return aVal < bVal ? 1 : -1
      }
    })

    // Calculate pagination
    const totalPages = Math.ceil(filtered.length / limit)
    const startIdx = (page - 1) * limit
    const paginatedData = filtered.slice(startIdx, startIdx + limit)

    return { filteredAndSorted: paginatedData, totalPages }
  }, [publications, yearFilter, typeFilter, themeFilter, sortBy, sortOrder, page, limit])

  // Extract unique values for filter dropdowns
  const availableYears = useMemo(() => {
    if (!publications) return []
    return Array.from(
      new Set(
        publications
          .map((p) => (p.date_publication ? new Date(p.date_publication).getFullYear() : null))
          .filter(Boolean)
      )
    ).sort((a: any, b: any) => b - a)
  }, [publications])

  const availableTypes = useMemo(() => {
    if (!publications) return []
    return Array.from(new Set(publications.map((p) => p.type_publication).filter(Boolean)))
  }, [publications])

  const availableThemes = useMemo(() => {
    if (!publications) return []
    return Array.from(
      new Set(publications.flatMap((p) => p.themes?.map((t: any) => t.label) || []))
    )
  }, [publications])

  // Empty state
  if (!publications || publications.length === 0) {
    return (
      <div className="text-center py-12">
        <BookOpen className="w-16 h-16 mx-auto text-gray-300 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          No publications found
        </h3>
        <p className="text-gray-500">This author has no publications yet</p>
      </div>
    )
  }

  // No results after filtering
  if (filteredAndSorted.length === 0 && (yearFilter || typeFilter || themeFilter)) {
    return (
      <div className="text-center py-12">
        <BookOpen className="w-16 h-16 mx-auto text-gray-300 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          No publications found
        </h3>
        <p className="text-gray-500">Try adjusting your filters</p>
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
            value={yearFilter || ''}
            onChange={(e) =>
              updateParams({
                year: e.target.value || undefined,
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
            value={typeFilter || ''}
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
            value={themeFilter || ''}
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
            value={sortBy || 'date'}
            onChange={(e) =>
              updateParams({
                sort_by: e.target.value,
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
          Showing {filteredAndSorted.length} of {publications.length} publications
        </p>
        <select
          className="w-24 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          value={limit.toString()}
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
        {filteredAndSorted.map((publication) => (
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
      {totalPages > 1 && (
        <div className="flex justify-center">
          <Pagination
            currentPage={page}
            totalPages={totalPages}
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
