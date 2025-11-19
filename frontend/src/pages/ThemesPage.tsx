/**
 * ThemesPage - List of AI research themes
 *
 * Displays research themes in a hierarchical structure with:
 * - Theme cards showing name, description, and publication count
 * - Search functionality
 * - Hierarchy level badges
 * - Navigation to publications filtered by theme
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useThemes } from '@/hooks/useThemes'
import { Card } from '@/components/common/Card'
import { Input } from '@/components/common/Input'
import { Button } from '@/components/common/Button'
import { Badge } from '@/components/common/Badge'
import { Loader } from '@/components/common/Loader'
import { Alert } from '@/components/common/Alert'
import { Search, BookOpen, Tag } from 'lucide-react'
import type { Theme } from '@/types/api'

export const ThemesPage = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const { data: themes, isLoading, isError, error } = useThemes()
  const navigate = useNavigate()

  // Filter themes based on search query
  const filteredThemes =
    themes?.filter((theme) =>
      theme.label.toLowerCase().includes(searchQuery.toLowerCase())
    ) || []

  // Group themes by hierarchy level for better organization
  const level1Themes = filteredThemes.filter((t) => t.niveau_hierarchie === 1)
  const displayThemes = searchQuery ? filteredThemes : level1Themes

  const handleViewPublications = (themeId: string) => {
    navigate(`/publications/search?theme=${themeId}`)
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Tag className="w-8 h-8 text-indigo-600" />
          <h1 className="text-3xl font-bold text-gray-900">Thèmes de recherche</h1>
        </div>
        <p className="text-gray-600">
          Explorez les thématiques de recherche en IA organisées par discipline et hiérarchie
        </p>
      </div>

      {/* Search Bar */}
      <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <Input
            type="text"
            placeholder="Rechercher des thèmes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex justify-center items-center py-12">
          <Loader size="lg" />
        </div>
      )}

      {/* Error State */}
      {isError && (
        <Alert variant="error">
          Erreur de chargement des thèmes : {error?.message || 'Erreur inconnue'}
        </Alert>
      )}

      {/* Results */}
      {!isLoading && !isError && (
        <>
          {/* Results Count */}
          <div className="mb-4">
            <p className="text-sm text-gray-600">
              {searchQuery
                ? `${displayThemes.length} thème${displayThemes.length !== 1 ? 's' : ''} trouvé${displayThemes.length !== 1 ? 's' : ''}`
                : `${displayThemes.length} discipline${displayThemes.length !== 1 ? 's' : ''} principale${displayThemes.length !== 1 ? 's' : ''}`}
            </p>
          </div>

          {/* Themes Grid */}
          {displayThemes.length === 0 ? (
            <div className="text-center py-12">
              <Tag className="w-16 h-16 mx-auto text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Aucun thème trouvé
              </h3>
              <p className="text-gray-500">
                {searchQuery
                  ? `Aucun thème ne correspond à "${searchQuery}"`
                  : 'Aucun thème disponible'}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {displayThemes.map((theme) => (
                <ThemeCard
                  key={theme.id}
                  theme={theme}
                  onViewPublications={handleViewPublications}
                />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}

interface ThemeCardProps {
  theme: Theme
  onViewPublications: (themeId: string) => void
}

const ThemeCard = ({ theme, onViewPublications }: ThemeCardProps) => {
  return (
    <Card
      className="hover:shadow-lg transition-shadow duration-200 cursor-pointer group"
      data-testid="theme-card"
    >
      <div className="p-6">
        {/* Header with Title and Level Badge */}
        <div className="flex justify-between items-start mb-3">
          <h3 className="text-xl font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors">
            {theme.label}
          </h3>
          <Badge variant="info" className="ml-2 flex-shrink-0">
            Niveau {theme.niveau_hierarchie}
          </Badge>
        </div>

        {/* Description */}
        {theme.description && (
          <p className="text-gray-600 text-sm mb-4 line-clamp-2">
            {theme.description}
          </p>
        )}

        {/* Footer with Stats and Action */}
        <div className="flex justify-between items-center mt-4 pt-4 border-t border-gray-100">
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <BookOpen className="w-4 h-4" />
            <span className="font-medium">
              {theme.nombre_publications.toLocaleString()}
            </span>
            <span>publication{theme.nombre_publications !== 1 ? 's' : ''}</span>
          </div>

          <Button
            size="sm"
            variant="ghost"
            onClick={() => onViewPublications(theme.id)}
            className="text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50"
          >
            Voir
          </Button>
        </div>
      </div>
    </Card>
  )
}

export default ThemesPage
