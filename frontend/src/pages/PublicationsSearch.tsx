/**
 * PublicationsSearch Page (Phase 4 - Step 5)
 *
 * Main page for searching publications with advanced filters.
 */

import { useState } from 'react'
import { SearchBar } from '@/components/search/SearchBar'
import { SearchFilters } from '@/components/search/SearchFilters'
import { SearchResults } from '@/components/search/SearchResults'
import { SearchPagination } from '@/components/search/SearchPagination'
import { PublicationModal } from '@/components/search/PublicationModal'
import { usePublicationSearch } from '@/hooks/usePublicationSearch'
import { publicationsApi } from '@/api/publications'
import type { PublicationDetailed } from '@/types/publication'

export const PublicationsSearch = () => {
  const { data, isLoading, error, queryParams, updateSearch } =
    usePublicationSearch()

  const [selectedPublication, setSelectedPublication] =
    useState<PublicationDetailed | null>(null)
  const [modalOpen, setModalOpen] = useState(false)

  const handleSearch = (query: string) => {
    updateSearch({ q: query, page: 1 })
  }

  const handleFilterChange = (filters: typeof queryParams) => {
    updateSearch({ ...filters, page: 1 })
  }

  const handleResetFilters = () => {
    updateSearch({
      q: queryParams.q,
      theme: undefined,
      type: undefined,
      organization: undefined,
      date_from: undefined,
      date_to: undefined,
      sort_by: 'date',
      sort_order: 'desc',
      page: 1,
    })
  }

  const handlePageChange = (page: number) => {
    updateSearch({ page })
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleViewDetails = async (id: string) => {
    try {
      const publication = await publicationsApi.getById(id)
      setSelectedPublication(publication)
      setModalOpen(true)
    } catch (err) {
      console.error('Error loading publication details:', err)
    }
  }

  const handleCloseModal = () => {
    setModalOpen(false)
    setSelectedPublication(null)
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Recherche de Publications
        </h1>
        <p className="text-gray-600">
          Explorez notre base de données de publications en Intelligence
          Artificielle
        </p>
      </div>

      {/* Search Bar */}
      <div className="mb-6">
        <SearchBar
          initialValue={queryParams.q}
          onSearch={handleSearch}
          placeholder="Rechercher par titre, résumé, auteur..."
        />
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Filters Sidebar */}
        <div className="lg:col-span-1">
          <SearchFilters
            filters={queryParams}
            onFilterChange={handleFilterChange}
            onReset={handleResetFilters}
          />
        </div>

        {/* Results */}
        <div className="lg:col-span-3">
          <SearchResults
            publications={data?.items || []}
            loading={isLoading}
            error={error}
            total={data?.total || 0}
            onViewDetails={handleViewDetails}
          />

          {/* Pagination */}
          {data && (
            <SearchPagination
              currentPage={data.page}
              totalPages={data.total_pages}
              onPageChange={handlePageChange}
            />
          )}
        </div>
      </div>

      {/* Details Modal */}
      <PublicationModal
        publication={selectedPublication}
        isOpen={modalOpen}
        onClose={handleCloseModal}
      />
    </div>
  )
}
