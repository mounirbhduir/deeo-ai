/**
 * API functions for graphs (Phase 4 - Step 8)
 */

import { apiClient } from './client'
import type { GraphData, CollaborationGraphFilters, AffiliationGraphFilters } from '@/types/graph'

export const graphsApi = {
  /**
   * Get collaboration graph (co-authorship)
   */
  getCollaborationGraph: async (filters: CollaborationGraphFilters = {}): Promise<GraphData> => {
    const params = new URLSearchParams()

    if (filters.min_collaborations !== undefined) {
      params.append('min_collaborations', String(filters.min_collaborations))
    }
    if (filters.theme) {
      params.append('theme', filters.theme)
    }
    if (filters.year_from) {
      params.append('year_from', String(filters.year_from))
    }
    if (filters.year_to) {
      params.append('year_to', String(filters.year_to))
    }

    const { data } = await apiClient.get<GraphData>(`/graphs/collaboration?${params.toString()}`)
    return data
  },

  /**
   * Get affiliation graph (author-organisation)
   */
  getAffiliationGraph: async (filters: AffiliationGraphFilters = {}): Promise<GraphData> => {
    const params = new URLSearchParams()

    if (filters.include_authors !== undefined) {
      params.append('include_authors', String(filters.include_authors))
    }
    if (filters.include_organisations !== undefined) {
      params.append('include_organisations', String(filters.include_organisations))
    }

    const { data } = await apiClient.get<GraphData>(`/graphs/affiliation?${params.toString()}`)
    return data
  },

  /**
   * Get graph statistics
   */
  getStatistics: async (graphType: 'collaboration' | 'affiliation' = 'collaboration'): Promise<GraphData['statistics']> => {
    const { data } = await apiClient.get(`/graphs/statistics?graph_type=${graphType}`)
    return data
  },
}
