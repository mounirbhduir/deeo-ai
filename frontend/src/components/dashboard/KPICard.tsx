import { ReactNode } from 'react'
import { Card } from '@/components/common/Card'
import { Badge } from '@/components/common/Badge'
import { Skeleton } from '@/components/common/Skeleton'
import { TrendingUp, TrendingDown } from 'lucide-react'

export interface KPICardProps {
  title: string
  value: string | number
  icon: ReactNode
  trend?: {
    value: number
    isPositive: boolean
  }
  isLoading?: boolean
}

export function KPICard({
  title,
  value,
  icon,
  trend,
  isLoading = false,
}: KPICardProps) {
  if (isLoading) {
    return (
      <Card variant="bordered" padding="md">
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Skeleton variant="circular" width="24px" height="24px" />
            <Skeleton width="120px" height="16px" />
          </div>
          <Skeleton width="80px" height="32px" />
          <Skeleton width="60px" height="20px" />
        </div>
      </Card>
    )
  }

  // Format large numbers with thousands separator
  const formatValue = (val: string | number): string => {
    if (typeof val === 'number') {
      return val.toLocaleString('fr-FR')
    }
    return val
  }

  return (
    <Card
      variant="bordered"
      padding="md"
      className="hover:shadow-md transition-shadow"
    >
      <div className="flex flex-col gap-3">
        {/* Header: Icon + Title */}
        <div className="flex items-center gap-2 text-gray-600">
          <div className="text-blue-600">{icon}</div>
          <h3 className="text-sm font-medium">{title}</h3>
        </div>

        {/* Value */}
        <div className="text-3xl font-bold text-gray-900">
          {formatValue(value)}
        </div>

        {/* Trend Badge (optional) */}
        {trend && (
          <div className="flex items-center gap-1">
            <Badge
              variant={trend.isPositive ? 'success' : 'error'}
              size="sm"
              className="flex items-center gap-1"
            >
              {trend.isPositive ? (
                <TrendingUp className="w-3 h-3" />
              ) : (
                <TrendingDown className="w-3 h-3" />
              )}
              <span>{Math.abs(trend.value)}%</span>
            </Badge>
            <span className="text-xs text-gray-500">vs. mois dernier</span>
          </div>
        )}
      </div>
    </Card>
  )
}
