/**
 * useAuthorsSearch Hook (Phase 4 - Step 6)
 *
 * Custom hook for searching/listing authors with URL state synchronization.
 * Manages search query, sorting, and pagination.
 */

import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import { useMemo, useCallback } from 'react'
import { authorsApi } from '@/api/authors'
import type { AuthorSearchParams, AuthorSearchResponse } from '@/types/author'

/**
 * Parse URL search params to typed author search parameters
 */
const parseSearchParams = (searchParams: URLSearchParams): AuthorSearchParams => {
  return {
    search: searchParams.get('search') || undefined,
    sort_by:
      (searchParams.get('sort_by') as 'nom' | 'h_index' | 'citations') || 'nom',
    order: (searchParams.get('order') as 'asc' | 'desc') || 'asc',
    page: parseInt(searchParams.get('page') || '1', 10),
    limit: parseInt(searchParams.get('limit') || '20', 10),
  }
}

/**
 * Hook for author search/list with URL state management
 * @returns Authors data, loading state, error, params, and update function
 */
export const useAuthorsSearch = () => {
  const [searchParams, setSearchParams] = useSearchParams()

  // Parse current URL params
  const queryParams = useMemo(
    () => parseSearchParams(searchParams),
    [searchParams]
  )

  // Fetch authors with React Query
  const query = useQuery<AuthorSearchResponse>({
    queryKey: ['authors-search', queryParams],
    queryFn: () => authorsApi.getAll(queryParams),
    staleTime: 1000 * 60, // 1 minute
    retry: 1,
  })

  // Update search params (and trigger new fetch via queryKey change)
  const updateSearch = useCallback(
    (newParams: Partial<AuthorSearchParams>) => {
      const updatedParams = new URLSearchParams(searchParams)

      Object.entries(newParams).forEach(([key, value]) => {
        if (value === undefined || value === null || value === '') {
          updatedParams.delete(key)
        } else {
          updatedParams.set(key, String(value))
        }
      })

      setSearchParams(updatedParams)
    },
    [searchParams, setSearchParams]
  )

  return {
    data: query.data,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    queryParams,
    updateSearch,
  }
}
