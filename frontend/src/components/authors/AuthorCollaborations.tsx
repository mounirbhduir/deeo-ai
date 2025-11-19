/**
 * AuthorCollaborations Component (Phase 4 - Step 6)
 *
 * Displays top co-authors with collaboration counts.
 * Shows avatars, names, and number of shared publications.
 */

import { Link } from 'react-router-dom'
import { Users } from 'lucide-react'
import { Card } from '@/components/common/Card'
import { Avatar } from '@/components/common/Avatar'
import { Progress } from '@/components/common/Progress'
import { getInitials } from '@/utils/stringUtils'
import type { CoAuthor } from '@/types/author'

interface AuthorCollaborationsProps {
  coauthors: CoAuthor[]
  title?: string
}

export const AuthorCollaborations = ({
  coauthors,
  title = 'Top Collaborators',
}: AuthorCollaborationsProps) => {
  if (coauthors.length === 0) {
    return (
      <Card>
        <div className="p-8 text-center text-gray-500">
          <Users className="w-12 h-12 mx-auto mb-2 text-gray-400" />
          <p>No collaborations found</p>
        </div>
      </Card>
    )
  }

  const maxCollaborations = Math.max(
    ...coauthors.map((c) => c.collaborations_count)
  )

  return (
    <Card>
      <div className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Users className="w-5 h-5 text-indigo-600" />
          {title}
        </h3>

        <div className="space-y-4">
          {coauthors.map((coauthor) => {
            const fullName = `${coauthor.prenom} ${coauthor.nom}`
            const percentage = (coauthor.collaborations_count / maxCollaborations) * 100

            return (
              <Link
                key={coauthor.id}
                to={`/authors/${coauthor.id}`}
                className="block hover:bg-gray-50 -mx-2 px-2 py-2 rounded-lg transition-colors"
              >
                <div className="flex items-center gap-3 mb-2">
                  <Avatar alt={fullName} fallback={getInitials(fullName)} size="sm" />
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-gray-900 truncate">
                      {fullName}
                    </div>
                    <div className="text-sm text-gray-500">
                      {coauthor.collaborations_count}{' '}
                      {coauthor.collaborations_count === 1
                        ? 'publication'
                        : 'publications'}
                    </div>
                  </div>
                  <div className="text-sm font-semibold text-indigo-600">
                    {coauthor.collaborations_count}
                  </div>
                </div>
                <Progress value={percentage} className="h-2" />
              </Link>
            )
          })}
        </div>
      </div>
    </Card>
  )
}
