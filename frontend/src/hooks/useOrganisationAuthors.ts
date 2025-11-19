/**
 * useOrganisationAuthors Hook (Phase 4 - Step 7)
 *
 * Custom hook for fetching organisation's authors with URL state synchronization.
 */

import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import { useMemo, useCallback } from 'react'
import { organisationsApi } from '@/api/organisations'
import type {
  OrganisationAuthorsParams,
  OrganisationAuthorsResponse,
} from '@/types/organisation'

const parseAuthorsParams = (
  searchParams: URLSearchParams
): OrganisationAuthorsParams => {
  return {
    sort_by: (searchParams.get('sort_by') as 'nom' | 'h_index' | 'publications') || 'nom',
    order: (searchParams.get('order') as 'asc' | 'desc') || 'asc',
    page: parseInt(searchParams.get('page') || '1', 10),
    limit: parseInt(searchParams.get('limit') || '20', 10),
  }
}

export const useOrganisationAuthors = (organisationId: string | undefined) => {
  const [searchParams, setSearchParams] = useSearchParams()

  const queryParams = useMemo(
    () => parseAuthorsParams(searchParams),
    [searchParams]
  )

  const query = useQuery<OrganisationAuthorsResponse>({
    queryKey: ['organisation-authors', organisationId, queryParams],
    queryFn: () => organisationsApi.getAuthors(organisationId!, queryParams),
    enabled: !!organisationId,
    staleTime: 1000 * 60, // 1 minute
    retry: 1,
  })

  const updateParams = useCallback(
    (newParams: Partial<OrganisationAuthorsParams>) => {
      const updatedParams = new URLSearchParams(searchParams)

      Object.entries(newParams).forEach(([key, value]) => {
        if (value === undefined || value === null) {
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
