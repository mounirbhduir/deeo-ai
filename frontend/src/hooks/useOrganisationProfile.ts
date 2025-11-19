/**
 * useOrganisationProfile Hook (Phase 4 - Step 7)
 *
 * Custom hook for fetching complete organisation profile data.
 */

import { useQuery } from '@tanstack/react-query'
import { organisationsApi } from '@/api/organisations'
import type { OrganisationProfile } from '@/types/organisation'

export const useOrganisationProfile = (
  organisationId: string | undefined,
  options?: { enabled?: boolean }
) => {
  return useQuery<OrganisationProfile>({
    queryKey: ['organisation-profile', organisationId],
    queryFn: () => organisationsApi.getById(organisationId!),
    enabled: !!organisationId && (options?.enabled !== false),
    staleTime: 1000 * 60 * 5, // 5 minutes
    retry: 1,
  })
}
