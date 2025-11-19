import { useState } from 'react'
import { AuthorCard } from '@/components/authors/AuthorCard'
import { Select } from '@/components/common/Select'
import { Input } from '@/components/common/Input'
import type { AuthorListItem } from '@/types/author'

interface OrganisationAuthorsProps {
  authors: AuthorListItem[]
}

export const OrganisationAuthors = ({ authors }: OrganisationAuthorsProps) => {
  const [sortBy, setSortBy] = useState<'nom' | 'h_index' | 'publications'>('h_index')
  const [searchQuery, setSearchQuery] = useState('')

  const filteredAndSortedAuthors = authors
    .filter(author => {
      if (!searchQuery) return true
      const query = searchQuery.toLowerCase()
      return (
        author.nom.toLowerCase().includes(query) ||
        author.prenom.toLowerCase().includes(query)
      )
    })
    .sort((a, b) => {
      if (sortBy === 'nom') {
        return `${a.nom} ${a.prenom}`.localeCompare(`${b.nom} ${b.prenom}`)
      }
      if (sortBy === 'h_index') {
        return (b.h_index || 0) - (a.h_index || 0)
      }
      return b.nombre_publications - a.nombre_publications
    })

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <Input
            type="text"
            placeholder="Search researchers by name..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="w-full sm:w-48">
          <Select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'nom' | 'h_index' | 'publications')}
            options={[
              { value: 'h_index', label: 'H-Index (High to Low)' },
              { value: 'publications', label: 'Publications (High to Low)' },
              { value: 'nom', label: 'Name (A-Z)' },
            ]}
          />
        </div>
      </div>

      {filteredAndSortedAuthors.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          No researchers found matching your criteria.
        </div>
      ) : (
        <>
          <div className="text-sm text-gray-500">
            Showing {filteredAndSortedAuthors.length} of {authors.length} researchers
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAndSortedAuthors.map((author) => (
              <AuthorCard key={author.id} author={author} />
            ))}
          </div>
        </>
      )}
    </div>
  )
}
