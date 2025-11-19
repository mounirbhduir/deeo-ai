/**
 * AuthorProfile Page (Phase 4 - Step 6)
 *
 * Complete author profile page with tabbed interface.
 * Displays overview (stats + charts + collaborations), publications, and timeline.
 */

import { useParams } from 'react-router-dom'
import { useAuthorProfile } from '@/hooks/useAuthorProfile'
import {
  AuthorHeader,
  AuthorStats,
  AuthorCharts,
  AuthorCollaborations,
  AuthorPublications,
  AuthorTimeline,
} from '@/components/authors'
import { Tabs } from '@/components/common/Tabs'
import { Skeleton } from '@/components/common/Skeleton'
import { Alert } from '@/components/common/Alert'
import { ArrowLeft } from 'lucide-react'
import { Link } from 'react-router-dom'

export const AuthorProfile = () => {
  const { id } = useParams<{ id: string }>()
  const { data: author, isLoading, isError, error } = useAuthorProfile(id)

  // Loading State
  if (isLoading) {
    return (
      <div>
        {/* Header Skeleton */}
        <div className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex gap-6">
              <Skeleton className="w-32 h-32 rounded-full flex-shrink-0" />
              <div className="flex-1 space-y-4">
                <Skeleton className="h-10 w-64" />
                <Skeleton className="h-6 w-48" />
                <div className="flex gap-2">
                  <Skeleton className="h-8 w-24" />
                  <Skeleton className="h-8 w-24" />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Content Skeleton */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-4 gap-4 mb-8">
            <Skeleton className="h-24" />
            <Skeleton className="h-24" />
            <Skeleton className="h-24" />
            <Skeleton className="h-24" />
          </div>
          <Skeleton className="h-96" />
        </div>
      </div>
    )
  }

  // Error State
  if (isError || !author) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Link
          to="/authors"
          className="inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-800 mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Authors
        </Link>
        <Alert variant="error">
          {error?.message || 'Author not found'}
        </Alert>
      </div>
    )
  }

  const tabs = [
    {
      id: 'overview',
      label: 'Overview',
      content: (
        <div className="space-y-8">
          {/* Stats Cards */}
          <AuthorStats author={author} />

          {/* Charts */}
          <AuthorCharts statistics={author.statistics} />

          {/* Collaborations */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <AuthorCollaborations coauthors={author.coauthors} />
            <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Research Impact
              </h3>
              <div className="space-y-4">
                <div>
                  <div className="text-sm text-gray-600 mb-1">
                    Average Citations per Paper
                  </div>
                  <div className="text-3xl font-bold text-indigo-600">
                    {author.nombre_publications > 0
                      ? Math.round(
                          author.nombre_citations / author.nombre_publications
                        )
                      : 0}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-600 mb-1">
                    Total Research Output
                  </div>
                  <div className="text-3xl font-bold text-purple-600">
                    {author.nombre_publications} papers
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-600 mb-1">h-index</div>
                  <div className="text-3xl font-bold text-pink-600">
                    {author.h_index}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 'publications',
      label: `Publications (${author.nombre_publications})`,
      content: <AuthorPublications authorId={author.id} />,
    },
    {
      id: 'timeline',
      label: 'Career Timeline',
      content: <AuthorTimeline author={author} />,
    },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Back Button */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <Link
            to="/authors"
            className="inline-flex items-center gap-2 text-indigo-600 hover:text-indigo-800"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Authors
          </Link>
        </div>
      </div>

      {/* Author Header */}
      <AuthorHeader author={author} />

      {/* Tabbed Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs tabs={tabs} defaultTab="overview" />
      </div>
    </div>
  )
}
