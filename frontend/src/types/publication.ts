/**
 * Publication Search Types (Phase 4 - Step 5)
 *
 * Extended types for the publications search feature with full relationships.
 */

export interface PublicationAuteur {
  id: string
  nom: string
  prenom: string
}

export interface PublicationOrganisation {
  id: string
  nom: string
}

export interface PublicationTheme {
  id: string
  label: string
}

export interface PublicationDetailed {
  id: string
  titre: string
  abstract: string
  doi?: string | null
  arxiv_id?: string | null
  date_publication: string
  type_publication: string
  nombre_citations: number
  auteurs: PublicationAuteur[]
  organisations: PublicationOrganisation[]
  themes: PublicationTheme[]
}

export interface PublicationSearchParams {
  q?: string
  theme?: string
  type?: string
  organization?: string
  date_from?: string
  date_to?: string
  sort_by?: 'date' | 'citations' | 'relevance'
  sort_order?: 'asc' | 'desc'
  page?: number
  limit?: number
}

export interface PublicationSearchResponse {
  items: PublicationDetailed[]
  total: number
  page: number
  limit: number
  total_pages: number
}
