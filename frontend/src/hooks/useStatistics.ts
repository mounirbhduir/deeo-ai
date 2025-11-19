import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/api/client'
import type { Statistics } from '@/types/api'

/**
 * Hook to fetch global statistics
 * @returns TanStack Query result with statistics data
 */
export const useStatistics = () => {
  return useQuery<Statistics>({
    queryKey: ['statistics'],
    queryFn: async () => {
      const { data } = await apiClient.get('/statistics')
      return data
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
    retry: 1,
  })
}
