/**
 * AuthorTimeline Component (Phase 4 - Step 6)
 *
 * Displays career timeline with affiliations and major publications.
 * Shows chronological progression of positions and key research milestones.
 */

import { Briefcase, Award } from 'lucide-react'
import { Card } from '@/components/common/Card'
import { Badge } from '@/components/common/Badge'
import type { AuthorProfile } from '@/types/author'

interface AuthorTimelineProps {
  author: AuthorProfile
}

export const AuthorTimeline = ({ author }: AuthorTimelineProps) => {
  // Sort affiliations by start date (most recent first)
  const sortedAffiliations = [...author.affiliations].sort((a, b) => {
    return new Date(b.date_debut).getTime() - new Date(a.date_debut).getTime()
  })

  // Get top 5 publications by citations for milestones
  const topPublications = [...author.publications]
    .sort((a, b) => b.nombre_citations - a.nombre_citations)
    .slice(0, 5)

  // Combine affiliations and publications into timeline events
  const events = [
    ...sortedAffiliations.map((aff) => ({
      type: 'affiliation' as const,
      date: aff.date_debut,
      endDate: aff.date_fin,
      title: aff.poste || 'Researcher',
      subtitle: aff.organisation.nom,
      orgType: aff.organisation.type,
    })),
    ...topPublications.map((pub) => ({
      type: 'publication' as const,
      date: pub.date_publication,
      title: pub.titre,
      subtitle: `${pub.nombre_citations} citations`,
      citations: pub.nombre_citations,
    })),
  ].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())

  return (
    <Card>
      <div className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">
          Career Timeline
        </h3>

        <div className="relative">
          {/* Vertical line */}
          <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-200" />

          {/* Events */}
          <div className="space-y-8">
            {events.map((event, idx) => (
              <div key={idx} className="relative pl-14">
                {/* Icon */}
                <div className="absolute left-0 top-0 w-12 h-12 bg-white border-2 border-gray-200 rounded-full flex items-center justify-center">
                  {event.type === 'affiliation' ? (
                    <Briefcase className="w-5 h-5 text-indigo-600" />
                  ) : (
                    <Award className="w-5 h-5 text-purple-600" />
                  )}
                </div>

                {/* Content */}
                <div>
                  <div className="text-sm text-gray-500 mb-1">
                    {new Date(event.date).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                    })}
                    {event.type === 'affiliation' && event.endDate && (
                      <span>
                        {' '}
                        -{' '}
                        {new Date(event.endDate).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                        })}
                      </span>
                    )}
                    {event.type === 'affiliation' && !event.endDate && (
                      <Badge variant="success" size="sm" className="ml-2">
                        Current
                      </Badge>
                    )}
                  </div>
                  <div className="font-medium text-gray-900 mb-1">
                    {event.title}
                  </div>
                  <div className="text-sm text-gray-600">{event.subtitle}</div>
                  {event.type === 'affiliation' && (
                    <Badge
                      variant={
                        event.orgType === 'academic'
                          ? 'primary'
                          : event.orgType === 'industry'
                          ? 'info'
                          : 'default'
                      }
                      size="sm"
                      className="mt-2"
                    >
                      {event.orgType}
                    </Badge>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Card>
  )
}
