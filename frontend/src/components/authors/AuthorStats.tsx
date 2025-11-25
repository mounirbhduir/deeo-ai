/**
 * AuthorStats Component (Phase 4 - Step 6)
 *
 * Displays key author metrics in 4 stat cards.
 * Publications, Citations, h-index, and Collaborations count.
 *
 * PHASE A: Added safe data handling for incomplete arXiv data
 */

import { BookOpen, Quote, Award, Users } from 'lucide-react'
import { Card } from '@/components/common/Card'
import type { AuthorProfile } from '@/types/author'
import { displayHIndex, displayCitations, hasData } from '@/utils/dataHelpers'

interface AuthorStatsProps {
  author: AuthorProfile
}

export const AuthorStats = ({ author }: AuthorStatsProps) => {
  const stats = [
    {
      label: 'Publications',
      value: author.nombre_publications || 0,
      icon: BookOpen,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      label: 'Citations',
      value: displayCitations(author.nombre_citations),
      icon: Quote,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      label: 'h-index',
      value: displayHIndex(author.h_index),
      icon: Award,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      label: 'Collaborations',
      value: hasData(author.coauthors) ? author.coauthors.length : 0,
      icon: Users,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
    },
  ]

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat) => {
        const Icon = stat.icon
        return (
          <Card key={stat.label} className="p-6">
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                <Icon className={`w-6 h-6 ${stat.color}`} />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">
                  {stat.value}
                </div>
                <div className="text-sm text-gray-500">{stat.label}</div>
              </div>
            </div>
          </Card>
        )
      })}
    </div>
  )
}
