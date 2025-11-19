import { useHealth } from '@/hooks/useHealth'

export function HealthCheck() {
  const { data, isLoading, error } = useHealth()

  if (isLoading) {
    return (
      <div className="flex items-center space-x-2">
        <div className="h-2 w-2 bg-gray-400 rounded-full animate-pulse" />
        <span className="text-sm text-gray-600">Vérification...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center space-x-2">
        <div className="h-2 w-2 bg-red-500 rounded-full" />
        <span className="text-sm text-red-600">API indisponible</span>
      </div>
    )
  }

  const isHealthy = data?.status === 'healthy'

  return (
    <div className="flex items-center space-x-2">
      <div
        className={`h-2 w-2 rounded-full ${
          isHealthy ? 'bg-green-500' : 'bg-yellow-500'
        }`}
      />
      <span
        className={`text-sm ${
          isHealthy ? 'text-green-600' : 'text-yellow-600'
        }`}
      >
        {isHealthy ? 'API opérationnelle' : 'API dégradée'}
      </span>
    </div>
  )
}
