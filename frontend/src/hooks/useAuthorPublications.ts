/**
 * useAuthorPublications Hook (Phase 4 - Step 6)
 *
 * Custom hook for fetching author's publications with URL state synchronization.
 * Manages filtering (year, type, theme), sorting, and pagination.
 */

import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import { useMemo, useCallback } from 'react'
import { authorsApi } from '@/api/authors'
import type {
  AuthorPublicationsParams,
  AuthorPublicationsResponse,
} from '@/types/author'

/**
 * Parse URL search params to typed publication filter parameters
 */
const parsePublicationParams = (
  searchParams: URLSearchParams
): AuthorPublicationsParams => {
  const yearStr = searchParams.get('year')
  const year = yearStr ? parseInt(yearStr, 10) : undefined

  return {
    year,
    type: searchParams.get('type') || undefined,
    theme: searchParams.get('theme') || undefined,
    sort_by:
      (searchParams.get('sort_by') as 'date' | 'citations' | 'titre') || 'date',
    order: (searchParams.get('order') as 'asc' | 'desc') || 'desc',
    page: parseInt(searchParams.get('page') || '1', 10),
    limit: parseInt(searchParams.get('limit') || '20', 10),
  }
}

/**
 * Hook for fetching author publications with URL state management
 * @param authorId - Author ID
 * @returns Publications data, loading state, error, params, and update function
 */
export const useAuthorPublications = (authorId: string | undefined) => {
  const [searchParams, setSearchParams] = useSearchParams()

  // Parse current URL params
  const queryParams = useMemo(
    () => parsePublicationParams(searchParams),
    [searchParams]
  )

  // Fetch publications with React Query
  const query = useQuery<AuthorPublicationsResponse>({
    queryKey: ['author-publications', authorId, queryParams],
    queryFn: () => authorsApi.getPublications(authorId!, queryParams),
    enabled: !!authorId,
    staleTime: 1000 * 60, // 1 minute
    retry: 1,
  })

  // Update params (and trigger new fetch via queryKey change)
  const updateParams = useCallback(
    (newParams: Partial<AuthorPublicationsParams>) => {
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
    updateParams,
  }
}
