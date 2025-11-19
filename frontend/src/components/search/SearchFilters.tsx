/**
 * SearchFilters Component (Phase 4 - Step 5)
 *
 * Advanced filters for publication search (type, theme, dates, sort).
 */

import { ChangeEvent, useMemo } from 'react'
import { Select } from '../common/Select'
import { Input } from '../common/Input'
import { Button } from '../common/Button'
import { useThemes } from '@/hooks/useThemes'
import type { PublicationSearchParams } from '@/types/publication'

interface SearchFiltersProps {
  filters: Partial<PublicationSearchParams>
  onFilterChange: (filters: Partial<PublicationSearchParams>) => void
  onReset: () => void
}

const PUBLICATION_TYPES = [
  { value: '', label: 'Tous les types' },
  { value: 'article', label: 'Article' },
  { value: 'preprint', label: 'Preprint' },
  { value: 'conference_paper', label: 'Conférence' },
  { value: 'journal_paper', label: 'Journal' },
  { value: 'thesis', label: 'Thèse' },
]

const SORT_OPTIONS = [
  { value: 'date', label: 'Date de publication' },
  { value: 'citations', label: 'Nombre de citations' },
  { value: 'relevance', label: 'Pertinence' },
]

export const SearchFilters = ({
  filters,
  onFilterChange,
  onReset,
}: SearchFiltersProps) => {
  // Fetch themes dynamically from API
  const { data: themesData } = useThemes({
    sort: '-nombre_publications',
    limit: 100,
  })

  // Build theme options from API data (ID as value, label as display)
  const themeOptions = useMemo(() => {
    const options = [{ value: '', label: 'Tous les thèmes' }]
    if (themesData) {
      themesData.forEach(theme => {
        options.push({
          value: theme.id, // Use theme ID as value (this is what backend expects)
          label: theme.label, // Use theme label for display
        })
      })
    }
    return options
  }, [themesData])

  const handleChange = (key: keyof PublicationSearchParams, value: string) => {
    onFilterChange({ [key]: value || undefined })
  }

  const hasActiveFilters = Object.entries(filters).some(
    ([key, value]) => value && key !== 'page' && key !== 'limit' && key !== 'sort_by' && key !== 'sort_order'
  )

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Filtres</h3>
        {hasActiveFilters && (
          <Button variant="ghost" size="sm" onClick={onReset}>
            Réinitialiser
          </Button>
        )}
      </div>

      <div className="space-y-4">
        {/* Type de publication */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Type de publication
          </label>
          <Select
            value={filters.type || ''}
            onChange={(e: ChangeEvent<HTMLSelectElement>) =>
              handleChange('type', e.target.value)
            }
            options={PUBLICATION_TYPES}
          />
        </div>

        {/* Thème */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Thème
          </label>
          <Select
            value={filters.theme || ''}
            onChange={(e: ChangeEvent<HTMLSelectElement>) =>
              handleChange('theme', e.target.value)
            }
            options={themeOptions}
          />
        </div>

        {/* Date range */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Période
          </label>
          <div className="grid grid-cols-2 gap-2">
            <Input
              type="text"
              value={filters.date_from || ''}
              onChange={(e: ChangeEvent<HTMLInputElement>) =>
                handleChange('date_from', e.target.value)
              }
              placeholder="De"
            />
            <Input
              type="text"
              value={filters.date_to || ''}
              onChange={(e: ChangeEvent<HTMLInputElement>) =>
                handleChange('date_to', e.target.value)
              }
              placeholder="À"
            />
          </div>
        </div>

        {/* Sort */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Trier par
          </label>
          <Select
            value={filters.sort_by || 'date'}
            onChange={(e: ChangeEvent<HTMLSelectElement>) =>
              handleChange('sort_by', e.target.value)
            }
            options={SORT_OPTIONS}
          />
        </div>

        {/* Sort order */}
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              name="sort_order"
              value="desc"
              checked={filters.sort_order !== 'asc'}
              onChange={(e: ChangeEvent<HTMLInputElement>) =>
                handleChange('sort_order', e.target.value)
              }
              className="text-indigo-600 focus:ring-indigo-500"
            />
            <span className="text-sm text-gray-700">Décroissant</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              name="sort_order"
              value="asc"
              checked={filters.sort_order === 'asc'}
              onChange={(e: ChangeEvent<HTMLInputElement>) =>
                handleChange('sort_order', e.target.value)
              }
              className="text-indigo-600 focus:ring-indigo-500"
            />
            <span className="text-sm text-gray-700">Croissant</span>
          </label>
        </div>
      </div>
    </div>
  )
}
