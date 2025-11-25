/**
 * AuthorsList Page (Phase 4 - Step 6)
 *
 * Page displaying a searchable, sortable, paginated list of authors.
 * Uses AuthorCard components in a responsive grid layout.
 */

import { useAuthorsSearch } from '@/hooks/useAuthorsSearch'
import { AuthorCard } from '@/components/authors'
import { Input } from '@/components/common/Input'
import { Pagination } from '@/components/common/Pagination'
import { Loader } from '@/components/common/Loader'
import { Alert } from '@/components/common/Alert'
import { Search, Users } from 'lucide-react'

export const AuthorsList = () => {
  const { data, isLoading, isError, error, queryParams, updateSearch } =
    useAuthorsSearch()

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Users className="w-8 h-8 text-indigo-600" />
          <h1 className="text-3xl font-bold text-gray-900">
            Chercheurs en IA
          </h1>
        </div>
        <p className="text-gray-600">
          Explorez les profils des chercheurs leaders en intelligence artificielle
        </p>
      </div>

      {/* Search & Filters */}
      <div className="bg-white border border-gray-200 rounded-lg p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Search Input */}
          <div className="relative md:col-span-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <Input
              type="text"
              placeholder="Rechercher par nom..."
              value={queryParams.search || ''}
              onChange={(e) =>
                updateSearch({ search: e.target.value, page: 1 })
              }
              className="pl-10"
            />
          </div>

          {/* Sort By */}
          <select
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            value={queryParams.sort_by || 'nom'}
            onChange={(e) =>
              updateSearch({
                sort_by: e.target.value as 'nom' | 'h_index' | 'citations' | 'nombre_publications',
              })
            }
            aria-label="Trier les auteurs par critère"
          >
            <option value="nom">Trier par nom</option>
            <option value="h_index">Trier par indice h</option>
            <option value="citations">Trier par citations</option>
            <option value="nombre_publications">Nombre de publications</option>
          </select>

          {/* Sort Order */}
          <select
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            value={queryParams.order || 'asc'}
            onChange={(e) =>
              updateSearch({ order: e.target.value as 'asc' | 'desc' })
            }
            aria-label="Ordre de tri"
          >
            <option value="asc">Croissant</option>
            <option value="desc">Décroissant</option>
          </select>
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
          Erreur de chargement des auteurs : {error?.message || 'Erreur inconnue'}
        </Alert>
      )}

      {/* Results */}
      {data && (
        <>
          {/* Results Count */}
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm text-gray-600">
              Affichage de {data.items.length} sur {data.total} auteurs
            </p>
            <select
              className="w-24 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              value={queryParams.limit?.toString() || '20'}
              onChange={(e) =>
                updateSearch({ limit: parseInt(e.target.value), page: 1 })
              }
              aria-label="Nombre d'auteurs par page"
            >
              <option value="12">12</option>
              <option value="24">24</option>
              <option value="48">48</option>
            </select>
          </div>

          {/* Authors Grid */}
          {data.items.length === 0 ? (
            <div className="text-center py-12">
              <Users className="w-16 h-16 mx-auto text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Aucun auteur trouvé
              </h3>
              <p className="text-gray-500">
                {queryParams.search
                  ? `Aucun auteur ne correspond à "${queryParams.search}"`
                  : 'Aucun auteur disponible'}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              {data.items.map((author) => (
                <AuthorCard key={author.id} author={author} />
              ))}
            </div>
          )}

          {/* Pagination */}
          {data.total_pages > 1 && (
            <div className="flex justify-center">
              <Pagination
                currentPage={queryParams.page || 1}
                totalPages={data.total_pages}
                onPageChange={(page) => updateSearch({ page })}
              />
            </div>
          )}
        </>
      )}
    </div>
  )
}
