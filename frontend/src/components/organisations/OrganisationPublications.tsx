import { useState } from 'react'
import { PublicationCard } from '@/components/search/PublicationCard'
import { PublicationModal } from '@/components/search/PublicationModal'
import { Select } from '@/components/common/Select'
import { Input } from '@/components/common/Input'
import { publicationsApi } from '@/api/publications'
import type { PublicationDetailed } from '@/types/publication'

interface OrganisationPublicationsProps {
  publications: PublicationDetailed[]
}

export const OrganisationPublications = ({ publications }: OrganisationPublicationsProps) => {
  const [sortBy, setSortBy] = useState<'date' | 'citations'>('date')
  const [searchQuery, setSearchQuery] = useState('')
  const [filterTheme, setFilterTheme] = useState<string>('')
  const [selectedPublication, setSelectedPublication] = useState<PublicationDetailed | null>(null)
  const [modalOpen, setModalOpen] = useState(false)

  const themes = Array.from(new Set(publications.flatMap(p => (p.themes || []).map(t => t.label)))).sort()

  const filteredAndSortedPublications = publications
    .filter(pub => {
      if (searchQuery) {
        const query = searchQuery.toLowerCase()
        if (!pub.titre.toLowerCase().includes(query) &&
            !pub.abstract?.toLowerCase().includes(query)) {
          return false
        }
      }
      if (filterTheme && !(pub.themes || []).some(t => t.label === filterTheme)) {
        return false
      }
      return true
    })
    .sort((a, b) => {
      if (sortBy === 'date') {
        return new Date(b.date_publication).getTime() - new Date(a.date_publication).getTime()
      }
      return (b.nombre_citations || 0) - (a.nombre_citations || 0)
    })

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <Input
              type="text"
              placeholder="Search publications by title or abstract..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <div className="w-full sm:w-48">
            <Select
              value={filterTheme}
              onChange={(e) => setFilterTheme(e.target.value)}
              options={[
                { value: '', label: 'All Themes' },
                ...themes.map(theme => ({ value: theme, label: theme }))
              ]}
            />
          </div>
          <div className="w-full sm:w-48">
            <Select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'date' | 'citations')}
              options={[
                { value: 'date', label: 'Most Recent' },
                { value: 'citations', label: 'Most Cited' }
              ]}
            />
          </div>
        </div>
      </div>

      {filteredAndSortedPublications.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          No publications found matching your criteria.
        </div>
      ) : (
        <>
          <div className="text-sm text-gray-500">
            Showing {filteredAndSortedPublications.length} of {publications.length} publications
          </div>
          <div className="space-y-4">
            {filteredAndSortedPublications.map((publication) => (
              <PublicationCard
                key={publication.id}
                publication={publication}
                onViewDetails={async () => {
                  try {
                    const fullPublication = await publicationsApi.getById(publication.id)
                    setSelectedPublication(fullPublication)
                    setModalOpen(true)
                  } catch (err) {
                    console.error('Error loading publication details:', err)
                  }
                }}
              />
            ))}
          </div>
        </>
      )}

      {/* Publication Details Modal */}
      <PublicationModal
        publication={selectedPublication}
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false)
          setSelectedPublication(null)
        }}
      />
    </div>
  )
}
