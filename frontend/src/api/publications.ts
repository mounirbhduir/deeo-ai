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
  // Build query string from params, excluding undefined/null/empty values
  const queryParams = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      queryParams.append(key, String(value))
    }
  })

  const { data } = await apiClient.get<PublicationSearchResponse>(
    `/publications/search?${queryParams.toString()}`
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
