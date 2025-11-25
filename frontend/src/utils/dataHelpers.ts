/**
 * Data Helpers - PHASE A: Frontend Fallbacks
 *
 * Safe transformation functions for handling incomplete arXiv data.
 * Provides default values for fields that may be null/undefined.
 *
 * Context: STAGING environment has 251 arXiv publications but lacks:
 * - h_index (null for all authors)
 * - nombre_citations (0 or null)
 * - organisations (empty)
 * - semantic_scholar_id (null)
 *
 * Date: 2025-11-24
 */

import type { Author, AuthorListItem, AuthorProfile, AuthorAffiliation, CoAuthor } from '../types/author';
import type { PublicationDetailed, PublicationAuteur, PublicationOrganisation, PublicationTheme } from '../types/publication';
import type { Organisation, OrganisationListItem, OrganisationProfile, OrganisationTopAuthor } from '../types/organisation';

// ============================================================================
// SAFE AUTHOR FUNCTIONS
// ============================================================================

/**
 * Safely transform author data with fallback values
 */
export const safeAuthor = (author: any): Author => {
  if (!author) {
    return {
      id: '0',
      nom: 'Inconnu',
      prenom: '',
      h_index: 0,
      nombre_publications: 0,
      nombre_citations: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
  }

  return {
    id: author.id ?? '0',
    nom: author.nom ?? 'Inconnu',
    prenom: author.prenom ?? '',
    email: author.email ?? undefined,
    orcid: author.orcid ?? undefined,
    google_scholar_id: author.google_scholar_id ?? undefined,
    homepage_url: author.homepage_url ?? undefined,
    h_index: author.h_index ?? 0,
    nombre_publications: author.nombre_publications ?? 0,
    nombre_citations: author.nombre_citations ?? 0,
    created_at: author.created_at ?? new Date().toISOString(),
    updated_at: author.updated_at ?? new Date().toISOString(),
  };
};

/**
 * Safely transform author list item with affiliations
 */
export const safeAuthorListItem = (author: any): AuthorListItem => {
  const baseAuthor = safeAuthor(author);
  return {
    ...baseAuthor,
    affiliations: Array.isArray(author?.affiliations)
      ? author.affiliations.map(safeAffiliation)
      : [],
  };
};

/**
 * Safely transform author profile with all relations
 */
export const safeAuthorProfile = (author: any): AuthorProfile => {
  const baseAuthor = safeAuthor(author);
  return {
    ...baseAuthor,
    affiliations: Array.isArray(author?.affiliations)
      ? author.affiliations.map(safeAffiliation)
      : [],
    publications: Array.isArray(author?.publications)
      ? author.publications.map(safePublication)
      : [],
    coauthors: Array.isArray(author?.coauthors)
      ? author.coauthors.map(safeCoAuthor)
      : [],
    statistics: {
      publications_by_year: author?.statistics?.publications_by_year ?? {},
      publications_by_theme: author?.statistics?.publications_by_theme ?? {},
      citations_by_year: author?.statistics?.citations_by_year ?? {},
    },
  };
};

/**
 * Safely transform affiliation
 */
export const safeAffiliation = (affiliation: any): AuthorAffiliation => {
  if (!affiliation) {
    return {
      organisation: {
        id: '0',
        nom: 'Organisation inconnue',
        type: 'academic',
      },
      date_debut: '',
      date_fin: null,
      poste: undefined,
    };
  }

  return {
    organisation: {
      id: affiliation.organisation?.id ?? '0',
      nom: affiliation.organisation?.nom ?? 'Organisation inconnue',
      type: affiliation.organisation?.type ?? 'academic',
    },
    date_debut: affiliation.date_debut ?? '',
    date_fin: affiliation.date_fin ?? null,
    poste: affiliation.poste ?? undefined,
  };
};

/**
 * Safely transform co-author
 */
export const safeCoAuthor = (coauthor: any): CoAuthor => {
  if (!coauthor) {
    return {
      id: '0',
      nom: 'Inconnu',
      prenom: '',
      collaborations_count: 0,
    };
  }

  return {
    id: coauthor.id ?? '0',
    nom: coauthor.nom ?? 'Inconnu',
    prenom: coauthor.prenom ?? '',
    collaborations_count: coauthor.collaborations_count ?? 0,
  };
};

// ============================================================================
// SAFE PUBLICATION FUNCTIONS
// ============================================================================

/**
 * Safely transform publication author (simplified)
 */
export const safePublicationAuteur = (auteur: any): PublicationAuteur => {
  if (!auteur) {
    return {
      id: '0',
      nom: 'Inconnu',
      prenom: '',
    };
  }

  return {
    id: auteur.id ?? '0',
    nom: auteur.nom ?? 'Inconnu',
    prenom: auteur.prenom ?? '',
  };
};

/**
 * Safely transform publication organisation
 */
export const safePublicationOrganisation = (org: any): PublicationOrganisation => {
  if (!org) {
    return {
      id: '0',
      nom: 'Organisation inconnue',
    };
  }

  return {
    id: org.id ?? '0',
    nom: org.nom ?? 'Organisation inconnue',
  };
};

/**
 * Safely transform publication theme
 */
export const safePublicationTheme = (theme: any): PublicationTheme => {
  if (!theme) {
    return {
      id: '0',
      label: 'Non classé',
    };
  }

  return {
    id: theme.id ?? '0',
    label: theme.label ?? 'Non classé',
  };
};

/**
 * Safely transform publication with all relations
 */
export const safePublication = (pub: any): PublicationDetailed => {
  if (!pub) {
    return {
      id: '0',
      titre: 'Sans titre',
      abstract: '',
      date_publication: '',
      type_publication: 'article',
      nombre_citations: 0,
      auteurs: [],
      organisations: [],
      themes: [],
    };
  }

  return {
    id: pub.id ?? '0',
    titre: pub.titre ?? 'Sans titre',
    abstract: pub.abstract ?? '',
    doi: pub.doi ?? null,
    arxiv_id: pub.arxiv_id ?? null,
    date_publication: pub.date_publication ?? '',
    type_publication: pub.type_publication ?? 'article',
    nombre_citations: pub.nombre_citations ?? 0,
    auteurs: Array.isArray(pub.auteurs)
      ? pub.auteurs.map(safePublicationAuteur)
      : [],
    organisations: Array.isArray(pub.organisations)
      ? pub.organisations.map(safePublicationOrganisation)
      : [],
    themes: Array.isArray(pub.themes)
      ? pub.themes.map(safePublicationTheme)
      : [],
  };
};

// ============================================================================
// SAFE ORGANISATION FUNCTIONS
// ============================================================================

/**
 * Safely transform organisation
 */
export const safeOrganisation = (org: any): Organisation => {
  if (!org) {
    return {
      id: '0',
      nom: 'Organisation inconnue',
      type: 'academic',
      pays: '',
      ville: '',
      nombre_publications: 0,
      nombre_chercheurs: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
  }

  return {
    id: org.id ?? '0',
    nom: org.nom ?? 'Organisation inconnue',
    nom_court: org.nom_court ?? undefined,
    type: org.type ?? 'academic',
    pays: org.pays ?? '',
    ville: org.ville ?? '',
    secteur: org.secteur ?? undefined,
    url: org.url ?? undefined,
    ranking_mondial: org.ranking_mondial ?? undefined,
    nombre_publications: org.nombre_publications ?? 0,
    nombre_chercheurs: org.nombre_chercheurs ?? 0,
    total_citations: org.total_citations ?? undefined,
    created_at: org.created_at ?? new Date().toISOString(),
    updated_at: org.updated_at ?? new Date().toISOString(),
  };
};

/**
 * Safely transform organisation list item
 */
export const safeOrganisationListItem = (org: any): OrganisationListItem => {
  return safeOrganisation(org);
};

/**
 * Safely transform top author for organisation
 */
export const safeOrganisationTopAuthor = (author: any): OrganisationTopAuthor => {
  if (!author) {
    return {
      id: '0',
      nom: 'Inconnu',
      prenom: '',
      h_index: 0,
      publications_count: 0,
    };
  }

  return {
    id: author.id ?? '0',
    nom: author.nom ?? 'Inconnu',
    prenom: author.prenom ?? '',
    h_index: author.h_index ?? 0,
    publications_count: author.publications_count ?? 0,
  };
};

/**
 * Safely transform organisation profile with all relations
 */
export const safeOrganisationProfile = (org: any): OrganisationProfile => {
  const baseOrg = safeOrganisation(org);
  return {
    ...baseOrg,
    authors: Array.isArray(org?.authors)
      ? org.authors.map(safeAuthorListItem)
      : [],
    publications: Array.isArray(org?.publications)
      ? org.publications.map(safePublication)
      : [],
    statistics: {
      publications_by_year: org?.statistics?.publications_by_year ?? {},
      publications_by_theme: org?.statistics?.publications_by_theme ?? {},
      top_authors: Array.isArray(org?.statistics?.top_authors)
        ? org.statistics.top_authors.map(safeOrganisationTopAuthor)
        : [],
    },
  };
};

// ============================================================================
// DISPLAY HELPERS
// ============================================================================

/**
 * Display a value with fallback for null/undefined/zero
 * @param value - Value to display
 * @param fallback - Fallback text (default: "N/A")
 * @param includeZero - Whether to display 0 or use fallback (default: false)
 */
export const displayValue = (
  value: any,
  fallback: string = 'N/A',
  includeZero: boolean = false
): string => {
  if (value === null || value === undefined) return fallback;
  if (typeof value === 'number' && value === 0 && !includeZero) return fallback;
  return String(value);
};

/**
 * Display h-index with special handling
 */
export const displayHIndex = (hIndex: number | null | undefined): string => {
  if (hIndex === null || hIndex === undefined || hIndex === 0) {
    return 'Non disponible';
  }
  return String(hIndex);
};

/**
 * Display citation count
 */
export const displayCitations = (citations: number | null | undefined): string => {
  if (citations === null || citations === undefined) {
    return 'N/A';
  }
  return String(citations);
};

/**
 * Display ranking with special handling
 */
export const displayRanking = (ranking: number | null | undefined): string => {
  if (ranking === null || ranking === undefined) {
    return 'Non classé';
  }
  return `#${ranking}`;
};

/**
 * Check if an array has data
 */
export const hasData = (arr: any[] | undefined | null): boolean => {
  return Array.isArray(arr) && arr.length > 0;
};

/**
 * Check if a value is enriched (not null/undefined/0)
 */
export const isEnriched = (value: any): boolean => {
  if (value === null || value === undefined) return false;
  if (typeof value === 'number' && value === 0) return false;
  if (typeof value === 'string' && value.trim() === '') return false;
  return true;
};

/**
 * Get enrichment status badge text
 */
export const getEnrichmentStatus = (author: any): string => {
  const hasHIndex = isEnriched(author?.h_index);
  const hasCitations = isEnriched(author?.nombre_citations);
  const hasAffiliations = hasData(author?.affiliations);

  if (hasHIndex && hasCitations && hasAffiliations) {
    return 'Enrichi';
  } else if (hasHIndex || hasCitations || hasAffiliations) {
    return 'Partiellement enrichi';
  } else {
    return 'Données arXiv uniquement';
  }
};

// ============================================================================
// EMPTY STATE MESSAGES
// ============================================================================

export const EMPTY_STATE_MESSAGES = {
  NO_ORGANISATIONS: 'Aucune organisation disponible pour le moment',
  NO_PUBLICATIONS: 'Aucune publication trouvée',
  NO_AUTHORS: 'Aucun auteur trouvé',
  NO_COLLABORATIONS: 'Aucune collaboration trouvée',
  NO_AFFILIATIONS: 'Affiliation non renseignée',
  DATA_NOT_ENRICHED: 'Ces données seront disponibles après enrichissement',
  HINDEX_NOT_AVAILABLE: 'H-index non disponible',
  CITATIONS_NOT_AVAILABLE: 'Citations non disponibles',
} as const;
