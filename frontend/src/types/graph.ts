/**
 * Graph-related TypeScript types for DEEO.AI frontend
 * Phase 4 - Step 8: Network Graphs (Relation Visualization)
 */

/**
 * Graph node (Author or Organisation)
 */
export interface GraphNode {
  id: string
  label: string
  type: 'author' | 'organisation'
  size: number
  metadata: Record<string, unknown>
}

/**
 * Graph edge (relationship)
 */
export interface GraphEdge {
  id: string
  source: string
  target: string
  weight: number
  type: 'coauthorship' | 'affiliation'
  metadata: Record<string, unknown>
}

/**
 * Community detected in graph
 */
export interface GraphCommunity {
  id: number
  label: string
  nodes: string[]
  size: number
}

/**
 * Graph statistics
 */
export interface GraphStatistics {
  total_nodes: number
  total_edges: number
  density: number
  average_degree: number
  clustering_coefficient: number
  communities: GraphCommunity[]
  centrality: Record<string, number>
}

/**
 * Complete graph data
 */
export interface GraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
  statistics: GraphStatistics
}

/**
 * Collaboration graph filters
 */
export interface CollaborationGraphFilters {
  min_collaborations?: number
  theme?: string
  year_from?: number
  year_to?: number
}

/**
 * Affiliation graph filters
 */
export interface AffiliationGraphFilters {
  include_authors?: boolean
  include_organisations?: boolean
}
