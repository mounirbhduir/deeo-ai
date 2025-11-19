/**
 * SearchPagination Component (Phase 4 - Step 5)
 *
 * Pagination wrapper for search results.
 */

import { Pagination } from '../common/Pagination'

interface SearchPaginationProps {
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
}

export const SearchPagination = ({
  currentPage,
  totalPages,
  onPageChange,
}: SearchPaginationProps) => {
  if (totalPages <= 1) return null

  return (
    <div className="mt-8 flex justify-center">
      <Pagination
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={onPageChange}
      />
    </div>
  )
}
