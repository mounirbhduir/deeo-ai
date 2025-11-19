import { useMemo } from 'react'
import { Card } from '@/components/common/Card'
import { Building2, Users, BookOpen, Award, TrendingUp } from 'lucide-react'
import type { OrganisationProfile } from '@/types/organisation'

interface TimelineEvent {
  year: number
  type: 'milestone' | 'publications' | 'researchers' | 'achievement'
  title: string
  description: string
  icon: typeof Building2
  color: string
}

export const OrganisationTimeline = ({ organisation }: { organisation: OrganisationProfile }) => {
  const timelineEvents = useMemo(() => {
    const events: TimelineEvent[] = []

    // Group publications by year
    const pubsByYear = organisation.publications.reduce((acc, pub) => {
      const year = new Date(pub.date_publication).getFullYear()
      acc[year] = (acc[year] || 0) + 1
      return acc
    }, {} as Record<number, number>)

    // Add publication milestones
    Object.entries(pubsByYear)
      .sort(([a], [b]) => parseInt(b) - parseInt(a))
      .slice(0, 5)
      .forEach(([year, count]) => {
        events.push({
          year: parseInt(year),
          type: 'publications',
          title: `${count} Publications`,
          description: `Published ${count} research papers in AI and related fields`,
          icon: BookOpen,
          color: 'text-blue-600',
        })
      })

    // Add current researchers count
    if (organisation.authors.length > 0) {
      const currentYear = new Date().getFullYear()
      events.push({
        year: currentYear,
        type: 'researchers',
        title: `${organisation.authors.length} Active Researchers`,
        description: 'Current research team strength',
        icon: Users,
        color: 'text-green-600',
      })
    }

    // Add ranking achievement if available
    if (organisation.ranking_mondial) {
      const currentYear = new Date().getFullYear()
      events.push({
        year: currentYear,
        type: 'achievement',
        title: `World Ranking #${organisation.ranking_mondial}`,
        description: 'Global recognition in AI research',
        icon: Award,
        color: 'text-yellow-600',
      })
    }

    // Add total citations milestone
    if (organisation.total_citations && organisation.total_citations > 0) {
      const currentYear = new Date().getFullYear()
      events.push({
        year: currentYear,
        type: 'achievement',
        title: `${organisation.total_citations.toLocaleString()} Citations`,
        description: 'Research impact across the scientific community',
        icon: TrendingUp,
        color: 'text-purple-600',
      })
    }

    return events.sort((a, b) => b.year - a.year)
  }, [organisation])

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-gray-900">Timeline & Milestones</h3>

      {timelineEvents.length === 0 ? (
        <Card className="p-8">
          <div className="text-center text-gray-500">
            No timeline data available.
          </div>
        </Card>
      ) : (
        <div className="relative">
          {/* Timeline line */}
          <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-200" />

          {/* Timeline events */}
          <div className="space-y-6">
            {timelineEvents.map((event, index) => {
              const Icon = event.icon
              return (
                <div key={index} className="relative flex gap-6">
                  {/* Icon */}
                  <div className="flex-shrink-0 w-16 h-16 bg-white border-4 border-gray-200 rounded-full flex items-center justify-center z-10">
                    <Icon className={`w-6 h-6 ${event.color}`} />
                  </div>

                  {/* Content */}
                  <Card className="flex-1">
                    <div className="p-6">
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="text-lg font-semibold text-gray-900">{event.title}</h4>
                        <span className="text-sm font-medium text-gray-500">{event.year}</span>
                      </div>
                      <p className="text-gray-600">{event.description}</p>
                    </div>
                  </Card>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
