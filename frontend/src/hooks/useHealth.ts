// src/hooks/useHealth.ts (VERSION CORRIGÉE)

import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

interface HealthResponse {
  status: string
  api: string
  database: string
  cache: string
}

async function fetchHealth(): Promise<HealthResponse> {
  // Utilise le proxy Vite configuré dans vite.config.ts
  // L'URL relative /api/health sera proxifiée vers http://localhost:8000/api/health
  const response = await axios.get('/api/health')
  return response.data
}

export function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
    refetchInterval: 30000, // Refetch every 30 seconds
    staleTime: 10000, // Consider stale after 10 seconds
    retry: 3, // Retry failed requests 3 times
  })
}