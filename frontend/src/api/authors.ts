/**
 * Authors API Service (Phase 4 - Step 6)
 *
 * Service for fetching author profiles, publications, and co-authors.
 */

import { apiClient } from './client'
import type {
  AuthorSearchParams,
  AuthorSearchResponse,
  AuthorProfile,
  AuthorPublicationsParams,
  AuthorPublicationsResponse,
  CoAuthor,
} from '@/types/author'

/**
 * Get paginated list of authors with search and sorting
 * @param params - Search and filter parameters
 * @returns Promise with paginated author list
 */
export const getAuthors = async (
  params: AuthorSearchParams = {}
): Promise<AuthorSearchResponse> => {
  // Build query string from params, excluding undefined/null/empty values
  const queryParams = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      queryParams.append(key, String(value))
    }
  })

  const { data } = await apiClient.get<AuthorSearchResponse>(
    `/authors?${queryParams.toString()}`
  )

  return data
}

/**
 * Get complete author profile by ID
 * @param id - Author ID
 * @returns Promise with complete author profile (includes publications, stats, co-authors)
 */
export const getAuthorById = async (id: string): Promise<AuthorProfile> => {
  const { data } = await apiClient.get<AuthorProfile>(`/authors/${id}`)
  return data
}

/**
 * Get author's publications with filtering and pagination
 * @param id - Author ID
 * @param params - Filter and pagination parameters
 * @returns Promise with paginated publications
 */
export const getAuthorPublications = async (
  id: string,
  params: AuthorPublicationsParams = {}
): Promise<AuthorPublicationsResponse> => {
  // Build query string from params
  const queryParams = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      queryParams.append(key, String(value))
    }
  })

  const { data } = await apiClient.get<AuthorPublicationsResponse>(
    `/authors/${id}/publications?${queryParams.toString()}`
  )

  return data
}

/**
 * Get author's top co-authors
 * @param id - Author ID
 * @param limit - Number of co-authors to return (default: 10)
 * @returns Promise with list of co-authors
 */
export const getAuthorCoAuthors = async (
  id: string,
  limit: number = 10
): Promise<CoAuthor[]> => {
  const { data } = await apiClient.get<CoAuthor[]>(
    `/authors/${id}/coauthors?limit=${limit}`
  )

  return data
}

/**
 * Export all author API functions as a single object
 */
export const authorsApi = {
  getAll: getAuthors,
  getById: getAuthorById,
  getPublications: getAuthorPublications,
  getCoAuthors: getAuthorCoAuthors,
}
