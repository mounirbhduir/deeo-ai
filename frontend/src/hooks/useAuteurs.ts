import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/api/client'
import type { Auteur } from '@/types/api'

export interface AuteursParams {
  sort?: string
  limit?: number
}

/**
 * Hook to fetch authors with optional sorting and limit
 * @param params - Query parameters (sort, limit)
 * @returns TanStack Query result with authors array
 */
export const useAuteurs = (params: AuteursParams = {}) => {
  return useQuery<Auteur[]>({
    queryKey: ['auteurs', params],
    queryFn: async () => {
      const { data } = await apiClient.get('/auteurs', { params })
      // Handle both array response and paginated response
      return Array.isArray(data) ? data : data.items || []
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
    retry: 1,
  })
}
