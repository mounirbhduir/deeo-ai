/**
 * Organisations API Service (Phase 4 - Step 7)
 *
 * Service for fetching organisation profiles, authors, and publications.
 */

import { apiClient } from './client'
import type {
  OrganisationSearchParams,
  OrganisationSearchResponse,
  OrganisationProfile,
  OrganisationAuthorsParams,
  OrganisationAuthorsResponse,
  OrganisationPublicationsParams,
  OrganisationPublicationsResponse,
} from '@/types/organisation'

/**
 * Get paginated list of organisations with search and sorting
 * @param params - Search and filter parameters
 * @returns Promise with paginated organisation list
 */
export const getOrganisations = async (
  params: OrganisationSearchParams = {}
): Promise<OrganisationSearchResponse> => {
  const queryParams = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      queryParams.append(key, String(value))
    }
  })

  const { data } = await apiClient.get<OrganisationSearchResponse>(
    `/organisations?${queryParams.toString()}`
  )

  return data
}

/**
 * Get complete organisation profile by ID
 * @param id - Organisation ID
 * @returns Promise with complete organisation profile
 */
export const getOrganisationById = async (id: string): Promise<OrganisationProfile> => {
  const { data } = await apiClient.get<OrganisationProfile>(`/organisations/${id}`)
  return data
}

/**
 * Get organisation's affiliated authors
 * @param id - Organisation ID
 * @param params - Filter and pagination parameters
 * @returns Promise with paginated authors
 */
export const getOrganisationAuthors = async (
  id: string,
  params: OrganisationAuthorsParams = {}
): Promise<OrganisationAuthorsResponse> => {
  const queryParams = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      queryParams.append(key, String(value))
    }
  })

  const { data } = await apiClient.get<OrganisationAuthorsResponse>(
    `/organisations/${id}/authors?${queryParams.toString()}`
  )

  return data
}

/**
 * Get organisation's publications
 * @param id - Organisation ID
 * @param params - Filter and pagination parameters
 * @returns Promise with paginated publications
 */
export const getOrganisationPublications = async (
  id: string,
  params: OrganisationPublicationsParams = {}
): Promise<OrganisationPublicationsResponse> => {
  const queryParams = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      queryParams.append(key, String(value))
    }
  })

  const { data } = await apiClient.get<OrganisationPublicationsResponse>(
    `/organisations/${id}/publications?${queryParams.toString()}`
  )

  return data
}

/**
 * Export all organisation API functions
 */
export const organisationsApi = {
  getAll: getOrganisations,
  getById: getOrganisationById,
  getAuthors: getOrganisationAuthors,
  getPublications: getOrganisationPublications,
}
