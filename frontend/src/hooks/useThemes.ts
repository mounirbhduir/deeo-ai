import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/api/client'
import type { Theme } from '@/types/api'

export interface ThemesParams {
  sort?: string
  limit?: number
}

/**
 * Hook to fetch themes with optional sorting and limit
 * @param params - Query parameters (sort, limit)
 * @returns TanStack Query result with themes array
 */
export const useThemes = (params: ThemesParams = {}) => {
  return useQuery<Theme[]>({
    queryKey: ['themes', params],
    queryFn: async () => {
      const { data } = await apiClient.get('/themes', { params })
      // Handle both array response and paginated response
      return Array.isArray(data) ? data : data.items || []
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
    retry: 1,
  })
}
