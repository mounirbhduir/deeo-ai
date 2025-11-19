import { Select } from '@/components/common/Select'
import { Input } from '@/components/common/Input'
import { Button } from '@/components/common/Button'
import { Pagination } from '@/components/common/Pagination'
import { OrganisationCard } from '@/components/organisations'
import { useOrganisationsSearch } from '@/hooks/useOrganisationsSearch'
import { Building2, Search, Filter, Loader2 } from 'lucide-react'
import { useState } from 'react'

export const OrganisationsList = () => {
  const { data, isLoading, isError, error, queryParams, updateSearch } = useOrganisationsSearch()
  const [localSearch, setLocalSearch] = useState(queryParams.search || '')

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    updateSearch({ search: localSearch, page: 1 })
  }

  const handleFilterChange = (key: string, value: string) => {
    updateSearch({ [key]: value || undefined, page: 1 })
  }

  const handlePageChange = (page: number) => {
    updateSearch({ page })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 bg-indigo-100 rounded-lg">
              <Building2 className="w-8 h-8 text-indigo-600" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Organisations de recherche en IA</h1>
              <p className="text-gray-600 mt-1">
                Explorez les universités, centres de recherche et entreprises leaders en intelligence artificielle
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <Filter className="w-5 h-5 text-gray-500" />
            <h2 className="text-lg font-semibold text-gray-900">Recherche & Filtres</h2>
          </div>

          <form onSubmit={handleSearchSubmit} className="space-y-4">
            <div className="flex gap-4">
              <div className="flex-1">
                <Input
                  type="search"
                  placeholder="Rechercher des organisations..."
                  value={localSearch}
                  onChange={(e) => setLocalSearch(e.target.value)}
                />
              </div>
              <Button type="submit">
                <Search className="w-4 h-4 mr-2" />
                Rechercher
              </Button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                <Select
                  value={queryParams.type || ''}
                  onChange={(e) => handleFilterChange('type', e.target.value)}
                  options={[
                    { value: '', label: 'Tous les types' },
                    { value: 'academic', label: 'Académique' },
                    { value: 'industry', label: 'Industrie' },
                    { value: 'research_center', label: 'Centre de recherche' },
                    { value: 'think_tank', label: 'Think Tank' }
                  ]}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Pays</label>
                <Select
                  value={queryParams.pays || ''}
                  onChange={(e) => handleFilterChange('pays', e.target.value)}
                  options={[
                    { value: '', label: 'Tous les pays' },
                    { value: 'USA', label: 'USA' },
                    { value: 'Canada', label: 'Canada' },
                    { value: 'UK', label: 'Royaume-Uni' },
                    { value: 'France', label: 'France' },
                    { value: 'Germany', label: 'Allemagne' },
                    { value: 'Switzerland', label: 'Suisse' },
                    { value: 'Israel', label: 'Israël' },
                    { value: 'China', label: 'Chine' }
                  ]}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Trier par</label>
                <Select
                  value={queryParams.sort_by || 'nom'}
                  onChange={(e) => handleFilterChange('sort_by', e.target.value)}
                  options={[
                    { value: 'nom', label: 'Nom' },
                    { value: 'publications', label: 'Publications' },
                    { value: 'chercheurs', label: 'Chercheurs' },
                    { value: 'ranking', label: 'Classement mondial' }
                  ]}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Ordre</label>
                <Select
                  value={queryParams.order || 'asc'}
                  onChange={(e) => handleFilterChange('order', e.target.value)}
                  options={[
                    { value: 'asc', label: 'Croissant' },
                    { value: 'desc', label: 'Décroissant' }
                  ]}
                />
              </div>
            </div>
          </form>
        </div>

        {/* Results */}
        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-indigo-600 animate-spin" />
          </div>
        )}

        {isError && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <p className="text-red-600">Erreur de chargement des organisations : {error?.message}</p>
          </div>
        )}

        {data && (
          <>
            <div className="mb-4 text-sm text-gray-600">
              Affichage de {data.items.length} sur {data.total} organisations
            </div>

            {data.items.length === 0 ? (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                <Building2 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Aucune organisation trouvée</h3>
                <p className="text-gray-500">Essayez d'ajuster vos critères de recherche</p>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                  {data.items.map((org) => (
                    <OrganisationCard key={org.id} organisation={org} />
                  ))}
                </div>

                {data.total_pages > 1 && (
                  <Pagination
                    currentPage={data.page}
                    totalPages={data.total_pages}
                    onPageChange={handlePageChange}
                  />
                )}
              </>
            )}
          </>
        )}
      </div>
    </div>
  )
}
