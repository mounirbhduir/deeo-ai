import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/api/client'
import type { Publication, PaginatedResponse } from '@/types/api'

export interface PublicationsParams {
  page?: number
  page_size?: number
  sort?: string
}

/**
 * Hook to fetch publications with pagination
 * @param params - Query parameters (page, page_size, sort)
 * @returns TanStack Query result with paginated publications
 */
export const usePublications = (params: PublicationsParams = {}) => {
  return useQuery<PaginatedResponse<Publication>>({
    queryKey: ['publications', params],
    queryFn: async () => {
      const { data } = await apiClient.get('/publications', { params })
      return data
    },
    staleTime: 1000 * 60, // 1 minute
    retry: 1,
  })
}
