/**
 * Publications API Service (Phase 4 - Step 5)
 *
 * Service for searching publications with advanced filters.
 */

import { apiClient } from './client'
import type {
  PublicationDetailed,
  PublicationSearchParams,
  PublicationSearchResponse,
} from '@/types/publication'

/**
 * Search publications with advanced filters
 * @param params - Search and filter parameters
 * @returns Promise with paginated search results
 */
export const searchPublications = async (
  params: PublicationSearchParams
): Promise<PublicationSearchResponse> => {
  // Build query parameters, filtering out undefined/null values
  const queryParams: Record<string, any> = {
    page: params.page || 1,
    limit: params.limit || 20,
  }

  if (params.q) queryParams.q = params.q
  if (params.theme) queryParams.theme = params.theme
  if (params.type) queryParams.type = params.type
  if (params.organization) queryParams.organization = params.organization
  if (params.date_from) queryParams.date_from = params.date_from
  if (params.date_to) queryParams.date_to = params.date_to
  if (params.sort_by) queryParams.sort_by = params.sort_by
  if (params.sort_order) queryParams.sort_order = params.sort_order

  // Use search endpoint with all filters
  const { data } = await apiClient.get<PublicationSearchResponse>(
    `/publications/search`,
    { params: queryParams }
  )

  return data
}

/**
 * Get a single publication by ID
 * @param id - Publication ID
 * @returns Promise with publication details
 */
export const getPublicationById = async (
  id: string
): Promise<PublicationDetailed> => {
  const { data } = await apiClient.get<PublicationDetailed>(
    `/publications/search/${id}`
  )

  return data
}

/**
 * Export all publication API functions
 */
export const publicationsApi = {
  search: searchPublications,
  getById: getPublicationById,
}
