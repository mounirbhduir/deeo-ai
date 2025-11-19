/**
 * usePublicationSearch Hook (Phase 4 - Step 5)
 *
 * Custom hook for publication search with URL state synchronization.
 * Manages search parameters, filters, pagination, and keeps them in sync with URL.
 */

import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import { useMemo, useCallback } from 'react'
import { publicationsApi } from '@/api/publications'
import type {
  PublicationSearchParams,
  PublicationSearchResponse,
} from '@/types/publication'

/**
 * Parse URL search params to typed search parameters
 */
const parseSearchParams = (searchParams: URLSearchParams): PublicationSearchParams => {
  return {
    q: searchParams.get('q') || undefined,
    theme: searchParams.get('theme') || undefined,
    type: searchParams.get('type') || undefined,
    organization: searchParams.get('organization') || undefined,
    date_from: searchParams.get('date_from') || undefined,
    date_to: searchParams.get('date_to') || undefined,
    sort_by: (searchParams.get('sort_by') as 'date' | 'citations' | 'relevance') || 'date',
    sort_order: (searchParams.get('sort_order') as 'asc' | 'desc') || 'desc',
    page: parseInt(searchParams.get('page') || '1', 10),
    limit: parseInt(searchParams.get('limit') || '20', 10),
  }
}

/**
 * Hook for publication search with URL state management
 * @returns Search data, loading state, error, params, and update function
 */
export const usePublicationSearch = () => {
  const [searchParams, setSearchParams] = useSearchParams()

  // Parse current URL params
  const queryParams = useMemo(
    () => parseSearchParams(searchParams),
    [searchParams]
  )

  // Fetch publications with React Query
  const query = useQuery<PublicationSearchResponse>({
    queryKey: ['publications-search', queryParams],
    queryFn: () => publicationsApi.search(queryParams),
    staleTime: 1000 * 30, // 30 seconds
    retry: 1,
  })

  // Update search params (and trigger new fetch via queryKey change)
  const updateSearch = useCallback(
    (newParams: Partial<PublicationSearchParams>) => {
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
