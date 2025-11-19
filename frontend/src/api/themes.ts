/**
 * Themes API Service
 *
 * Service for fetching research themes and their hierarchical relationships.
 */

import { apiClient } from './client'
import type { Theme } from '@/types/api'

export interface ThemesParams {
  sort?: string
  limit?: number
  niveau?: number
  parent_id?: string
}

/**
 * Get all themes with optional filtering
 * @param params - Filter and sort parameters
 * @returns Promise with themes array
 */
export const getThemes = async (
  params: ThemesParams = {}
): Promise<Theme[]> => {
  const queryParams = new URLSearchParams()

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      queryParams.append(key, String(value))
    }
  })

  const queryString = queryParams.toString()
  const url = queryString ? `/themes?${queryString}` : '/themes'

  const { data } = await apiClient.get<Theme[] | { items: Theme[] }>(url)

  // Handle both array response and paginated response
  return Array.isArray(data) ? data : data.items || []
}

/**
 * Get theme by ID
 * @param id - Theme ID
 * @returns Promise with theme details
 */
export const getThemeById = async (id: string): Promise<Theme> => {
  const { data } = await apiClient.get<Theme>(`/themes/${id}`)
  return data
}

/**
 * Get child themes for a parent theme
 * @param id - Parent theme ID
 * @returns Promise with array of child themes
 */
export const getThemeChildren = async (id: string): Promise<Theme[]> => {
  const { data } = await apiClient.get<Theme[]>(`/themes/${id}/children`)
  return Array.isArray(data) ? data : []
}

/**
 * Export all theme API functions as a single object
 */
export const themesApi = {
  getAll: getThemes,
  getById: getThemeById,
  getChildren: getThemeChildren,
}
