export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
export const APP_NAME = import.meta.env.VITE_APP_NAME || 'DEEO.AI'
export const APP_VERSION = import.meta.env.VITE_APP_VERSION || '1.0.0'

export const ROUTES = {
  HOME: '/',
  DASHBOARD: '/dashboard',
  SEARCH: '/publications/search',
  PUBLICATION_DETAIL: '/publications/:id',
  AUTEUR_PROFILE: '/auteurs/:id',
  ORGANISATION_PROFILE: '/organisations/:id',
  THEMES: '/themes',
  THEME_DETAIL: '/themes/:id',
} as const

export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  PAGE_SIZE_OPTIONS: [10, 20, 50, 100],
} as const
