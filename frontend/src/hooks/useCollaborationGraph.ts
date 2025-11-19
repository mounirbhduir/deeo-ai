/**
 * useCollaborationGraph Hook (Phase 4 - Step 8)
 */

import { useQuery } from '@tanstack/react-query'
import { graphsApi } from '@/api/graphs'
import type { GraphData, CollaborationGraphFilters } from '@/types/graph'

export const useCollaborationGraph = (filters: CollaborationGraphFilters = {}) => {
  return useQuery<GraphData>({
    queryKey: ['collaboration-graph', filters],
    queryFn: () => graphsApi.getCollaborationGraph(filters),
    staleTime: 1000 * 60 * 2, // 2 minutes
    retry: 1,
  })
}
