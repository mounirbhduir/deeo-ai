/**
 * useAuthorProfile Hook (Phase 4 - Step 6)
 *
 * Custom hook for fetching complete author profile data.
 * Includes publications, statistics, and co-authors.
 */

import { useQuery } from '@tanstack/react-query'
import { authorsApi } from '@/api/authors'
import type { AuthorProfile } from '@/types/author'

/**
 * Hook for fetching complete author profile
 * @param authorId - Author ID
 * @param options - React Query options (enabled, etc.)
 * @returns Author profile data, loading state, and error
 */
export const useAuthorProfile = (
  authorId: string | undefined,
  options?: { enabled?: boolean }
) => {
  return useQuery<AuthorProfile>({
    queryKey: ['author-profile', authorId],
    queryFn: () => authorsApi.getById(authorId!),
    enabled: !!authorId && (options?.enabled !== false),
    staleTime: 1000 * 60 * 5, // 5 minutes
    retry: 1,
  })
}
