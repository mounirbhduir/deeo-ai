/**
 * useOrganisationPublications Hook (Phase 4 - Step 7)
 *
 * Custom hook for fetching organisation's publications with URL state synchronization.
 */

import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import { useMemo, useCallback } from 'react'
import { organisationsApi } from '@/api/organisations'
import type {
  OrganisationPublicationsParams,
  OrganisationPublicationsResponse,
} from '@/types/organisation'

const parsePublicationsParams = (
  searchParams: URLSearchParams
): OrganisationPublicationsParams => {
  const yearStr = searchParams.get('year')
  const year = yearStr ? parseInt(yearStr, 10) : undefined

  return {
    year,
    type: searchParams.get('type') || undefined,
    theme: searchParams.get('theme') || undefined,
    sort_by: (searchParams.get('sort_by') as 'date' | 'citations' | 'titre') || 'date',
    order: (searchParams.get('order') as 'asc' | 'desc') || 'desc',
    page: parseInt(searchParams.get('page') || '1', 10),
    limit: parseInt(searchParams.get('limit') || '20', 10),
  }
}

export const useOrganisationPublications = (organisationId: string | undefined) => {
  const [searchParams, setSearchParams] = useSearchParams()

  const queryParams = useMemo(
    () => parsePublicationsParams(searchParams),
    [searchParams]
  )

  const query = useQuery<OrganisationPublicationsResponse>({
    queryKey: ['organisation-publications', organisationId, queryParams],
    queryFn: () => organisationsApi.getPublications(organisationId!, queryParams),
    enabled: !!organisationId,
    staleTime: 1000 * 60, // 1 minute
    retry: 1,
  })

  const updateParams = useCallback(
    (newParams: Partial<OrganisationPublicationsParams>) => {
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
