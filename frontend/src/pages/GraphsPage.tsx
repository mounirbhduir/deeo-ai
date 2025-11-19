/**
 * GraphsPage - Network Graph Visualization (Phase 4 - Step 8)
 */

import { useState } from 'react'
import { NetworkGraph } from '@/components/graphs/NetworkGraph'
import { useCollaborationGraph } from '@/hooks/useCollaborationGraph'
import { Select } from '@/components/common/Select'
import { Card } from '@/components/common/Card'
import { Button } from '@/components/common/Button'
import { Loader2, Network } from 'lucide-react'

export const GraphsPage = () => {
  const [minCollaborations, setMinCollaborations] = useState(1)

  const { data: graphData, isLoading, isError, error } = useCollaborationGraph({
    min_collaborations: minCollaborations,
  })

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-indigo-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Chargement du réseau de collaboration...</p>
        </div>
      </div>
    )
  }

  if (isError || !graphData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="p-8 max-w-md text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Erreur de chargement du graphe</h2>
          <p className="text-gray-600 mb-4">{error?.message || 'Échec du chargement des données du graphe'}</p>
          <Button onClick={() => window.location.reload()}>Recharger la page</Button>
        </Card>
      </div>
    )
  }

  const { statistics } = graphData

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 bg-indigo-100 rounded-lg">
              <Network className="w-8 h-8 text-indigo-600" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Réseau de collaboration en recherche IA</h1>
              <p className="text-gray-600 mt-1">
                Explorez les connexions et collaborations entre chercheurs en IA
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar - Statistics & Filters */}
          <div className="lg:col-span-1 space-y-6">
            {/* Statistics */}
            <Card className="p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Statistiques du réseau</h2>
              <div className="space-y-3">
                <div>
                  <div className="text-sm text-gray-500">Nœuds</div>
                  <div className="text-2xl font-bold text-gray-900">{statistics.total_nodes}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">Arêtes</div>
                  <div className="text-2xl font-bold text-gray-900">{statistics.total_edges}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">Densité</div>
                  <div className="text-2xl font-bold text-gray-900">{(statistics.density * 100).toFixed(1)}%</div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">Clustering moyen</div>
                  <div className="text-2xl font-bold text-gray-900">{statistics.clustering_coefficient.toFixed(3)}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">Communautés</div>
                  <div className="text-2xl font-bold text-gray-900">{statistics.communities.length}</div>
                </div>
              </div>
            </Card>

            {/* Filters */}
            <Card className="p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Filtres</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Collaborations minimales
                  </label>
                  <Select
                    value={String(minCollaborations)}
                    onChange={(e) => setMinCollaborations(parseInt(e.target.value))}
                    options={[
                      { value: '1', label: '1+' },
                      { value: '2', label: '2+' },
                      { value: '3', label: '3+' },
                      { value: '5', label: '5+' },
                    ]}
                  />
                </div>
              </div>
            </Card>

            {/* Top Researchers */}
            <Card className="p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Principaux chercheurs</h2>
              <div className="space-y-2">
                {Object.entries(statistics.centrality)
                  .slice(0, 5)
                  .map(([authorId, centrality]) => {
                    const node = graphData.nodes.find((n) => n.id === authorId)
                    return (
                      <div key={authorId} className="flex justify-between text-sm">
                        <span className="text-gray-700 truncate">{node?.label || authorId}</span>
                        <span className="text-gray-500">{(centrality * 100).toFixed(0)}%</span>
                      </div>
                    )
                  })}
              </div>
            </Card>
          </div>

          {/* Main Graph */}
          <div className="lg:col-span-3">
            <Card className="p-6">
              <div className="mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Réseau de collaboration</h2>
                <p className="text-sm text-gray-600 mt-1">
                  <span className="inline-flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-indigo-600"></span>
                    Auteur
                  </span>
                  <span className="ml-4 inline-flex items-center gap-2">
                    <span className="w-3 h-3 rounded-sm bg-green-600"></span>
                    Organisation
                  </span>
                </p>
              </div>
              <NetworkGraph data={graphData} />
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
