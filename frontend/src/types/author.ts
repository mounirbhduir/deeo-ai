/**
 * Author-related TypeScript types for DEEO.AI frontend
 * Phase 4 - Step 6: Author Profiles
 */

import { PublicationDetailed } from './publication';

/**
 * Base Author information
 */
export interface Author {
  id: string;
  nom: string;
  prenom: string;
  email?: string;
  orcid?: string;
  google_scholar_id?: string;
  homepage_url?: string;
  h_index: number;
  nombre_publications: number;
  nombre_citations: number;
  created_at: string;
  updated_at: string;
}

/**
 * Organization information in affiliations
 */
export interface AuthorOrganisation {
  id: string;
  nom: string;
  type: string;
}

/**
 * Author affiliation (current or past position)
 */
export interface AuthorAffiliation {
  organisation: AuthorOrganisation;
  date_debut: string;
  date_fin?: string | null;
  poste?: string;
}

/**
 * Co-author information with collaboration count
 */
export interface CoAuthor {
  id: string;
  nom: string;
  prenom: string;
  collaborations_count: number;
}

/**
 * Author statistics (all computed dynamically from publications)
 */
export interface AuthorStats {
  publications_by_year: Record<number, number>;
  publications_by_theme: Record<string, number>;
  citations_by_year: Record<number, number>;
}

/**
 * Complete author profile with all related data
 */
export interface AuthorProfile extends Author {
  affiliations: AuthorAffiliation[];
  publications: PublicationDetailed[];
  coauthors: CoAuthor[];
  statistics: AuthorStats;
}

/**
 * Author list item (used in search results)
 */
export interface AuthorListItem extends Author {
  affiliations: AuthorAffiliation[];
}

/**
 * Parameters for author search/list
 */
export interface AuthorSearchParams {
  page?: number;
  limit?: number;
  search?: string;
  sort_by?: 'nom' | 'h_index' | 'citations';
  order?: 'asc' | 'desc';
}

/**
 * Paginated author search response
 */
export interface AuthorSearchResponse {
  items: AuthorListItem[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

/**
 * Parameters for author publications endpoint
 */
export interface AuthorPublicationsParams {
  page?: number;
  limit?: number;
  year?: number;
  type?: string;
  theme?: string;
  sort_by?: 'date' | 'citations' | 'titre';
  order?: 'asc' | 'desc';
}

/**
 * Paginated author publications response
 */
export interface AuthorPublicationsResponse {
  items: PublicationDetailed[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}
