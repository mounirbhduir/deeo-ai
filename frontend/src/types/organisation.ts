/**
 * Organisation-related TypeScript types for DEEO.AI frontend
 * Phase 4 - Step 7: Organisation Profiles
 */

import { AuthorListItem } from './author';
import { PublicationDetailed } from './publication';

/**
 * Organisation types
 */
export type OrganisationType = 'academic' | 'industry' | 'research_center' | 'think_tank';

/**
 * Base Organisation information
 */
export interface Organisation {
  id: string;
  nom: string;
  nom_court?: string;
  type: OrganisationType;
  pays: string;
  ville: string;
  secteur?: string;
  url?: string;
  ranking_mondial?: number;
  nombre_publications: number;
  nombre_chercheurs: number;
  total_citations?: number;
  created_at: string;
  updated_at: string;
}

/**
 * Top author info for organisation statistics
 */
export interface OrganisationTopAuthor {
  id: string;
  nom: string;
  prenom: string;
  h_index: number;
  publications_count: number;
}

/**
 * Organisation statistics (all computed dynamically)
 */
export interface OrganisationStats {
  publications_by_year: Record<number, number>;
  publications_by_theme: Record<string, number>;
  top_authors: OrganisationTopAuthor[];
}

/**
 * Complete organisation profile with all related data
 */
export interface OrganisationProfile extends Organisation {
  authors: AuthorListItem[];
  publications: PublicationDetailed[];
  statistics: OrganisationStats;
}

/**
 * Organisation list item (used in search results)
 */
export interface OrganisationListItem extends Organisation {}

/**
 * Parameters for organisation search/list
 */
export interface OrganisationSearchParams {
  page?: number;
  limit?: number;
  search?: string;
  type?: OrganisationType;
  pays?: string;
  sort_by?: 'nom' | 'publications' | 'chercheurs' | 'ranking';
  order?: 'asc' | 'desc';
}

/**
 * Paginated organisation search response
 */
export interface OrganisationSearchResponse {
  items: OrganisationListItem[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

/**
 * Parameters for organisation authors endpoint
 */
export interface OrganisationAuthorsParams {
  page?: number;
  limit?: number;
  sort_by?: 'nom' | 'h_index' | 'publications';
  order?: 'asc' | 'desc';
}

/**
 * Paginated organisation authors response
 */
export interface OrganisationAuthorsResponse {
  items: AuthorListItem[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

/**
 * Parameters for organisation publications endpoint
 */
export interface OrganisationPublicationsParams {
  page?: number;
  limit?: number;
  year?: number;
  type?: string;
  theme?: string;
  sort_by?: 'date' | 'citations' | 'titre';
  order?: 'asc' | 'desc';
}

/**
 * Paginated organisation publications response
 */
export interface OrganisationPublicationsResponse {
  items: PublicationDetailed[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}
