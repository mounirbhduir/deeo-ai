/**
 * useOrganisationsSearch Hook (Phase 4 - Step 7)
 *
 * Custom hook for searching/listing organisations with URL state synchronization.
 */

import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import { useMemo, useCallback } from 'react'
import { organisationsApi } from '@/api/organisations'
import type { OrganisationSearchParams, OrganisationSearchResponse } from '@/types/organisation'

const parseSearchParams = (searchParams: URLSearchParams): OrganisationSearchParams => {
  return {
    search: searchParams.get('search') || undefined,
    type: (searchParams.get('type') as 'academic' | 'industry' | 'research_center' | 'think_tank') || undefined,
    pays: searchParams.get('pays') || undefined,
    sort_by: (searchParams.get('sort_by') as 'nom' | 'publications' | 'chercheurs' | 'ranking') || 'nom',
    order: (searchParams.get('order') as 'asc' | 'desc') || 'asc',
    page: parseInt(searchParams.get('page') || '1', 10),
    limit: parseInt(searchParams.get('limit') || '20', 10),
  }
}

export const useOrganisationsSearch = () => {
  const [searchParams, setSearchParams] = useSearchParams()

  const queryParams = useMemo(
    () => parseSearchParams(searchParams),
    [searchParams]
  )

  const query = useQuery<OrganisationSearchResponse>({
    queryKey: ['organisations-search', queryParams],
    queryFn: () => organisationsApi.getAll(queryParams),
    staleTime: 1000 * 60, // 1 minute
    retry: 1,
  })

  const updateSearch = useCallback(
    (newParams: Partial<OrganisationSearchParams>) => {
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
