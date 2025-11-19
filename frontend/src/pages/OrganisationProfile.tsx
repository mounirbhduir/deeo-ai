import { useParams, Link } from 'react-router-dom'
import { useOrganisationProfile } from '@/hooks/useOrganisationProfile'
import {
  OrganisationHeader,
  OrganisationStats,
  OrganisationCharts,
  OrganisationAuthors,
  OrganisationPublications,
  OrganisationTimeline
} from '@/components/organisations'
import { Tabs } from '@/components/common/Tabs'
import { Button } from '@/components/common/Button'
import { Loader2, ArrowLeft } from 'lucide-react'

export const OrganisationProfile = () => {
  const { organisationId } = useParams<{ organisationId: string }>()
  const { data: organisation, isLoading, isError, error } = useOrganisationProfile(organisationId)

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-indigo-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading organisation profile...</p>
        </div>
      </div>
    )
  }

  if (isError || !organisation) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 max-w-md text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Profile</h2>
          <p className="text-gray-600 mb-6">{error?.message || 'Organisation not found'}</p>
          <Link to="/organisations">
            <Button>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Organisations
            </Button>
          </Link>
        </div>
      </div>
    )
  }

  const tabs = [
    {
      id: 'overview',
      label: 'Overview',
      content: <OrganisationCharts statistics={organisation.statistics} />
    },
    {
      id: 'researchers',
      label: `Researchers (${organisation.authors.length})`,
      content: (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Research Team</h3>
          <OrganisationAuthors authors={organisation.authors} />
        </div>
      )
    },
    {
      id: 'publications',
      label: `Publications (${organisation.publications.length})`,
      content: (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Research Publications</h3>
          <OrganisationPublications publications={organisation.publications} />
        </div>
      )
    },
    {
      id: 'timeline',
      label: 'Timeline',
      content: (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <OrganisationTimeline organisation={organisation} />
        </div>
      )
    }
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      <OrganisationHeader organisation={organisation} />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-4">
          <Link to="/organisations">
            <Button variant="secondary" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Organisations
            </Button>
          </Link>
        </div>

        <div className="space-y-8">
          {/* Stats Overview */}
          <OrganisationStats organisation={organisation} />

          {/* Tabs */}
          <Tabs tabs={tabs} defaultTab="overview" />
        </div>
      </div>
    </div>
  )
}
