export interface ApiResponse<T> {
  data: T
  message?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface ApiError {
  detail: string
  status_code?: number
}

// Statistics
export interface Statistics {
  total_publications: number
  total_auteurs: number
  total_organisations: number
  publications_last_7_days: number
}

// Publication
export interface Publication {
  id: string
  titre: string
  abstract?: string
  doi?: string
  arxiv_id?: string
  date_publication: string
  nombre_citations: number
  auteurs?: string[]
  themes?: string[]
  organisation_id?: string
}

// Auteur
export interface Auteur {
  id: string
  nom: string
  prenom: string
  h_index: number
  nombre_publications: number
  nombre_citations: number
  organisation_id?: string
  domaines_expertise?: string[]
}

// Theme
export interface Theme {
  id: string
  label: string
  description?: string
  nombre_publications: number
  niveau_hierarchie: number
  parent_id?: string
}

// Organisation
export interface Organisation {
  id: string
  nom: string
  type_organisation: string
  pays: string
  nombre_publications: number
  nombre_chercheurs: number
  ville?: string
}
