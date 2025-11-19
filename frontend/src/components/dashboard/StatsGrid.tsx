import { ReactNode } from 'react'
import { KPICard } from './KPICard'

export interface KPIData {
  title: string
  value: string | number
  icon: ReactNode
  trend?: {
    value: number
    isPositive: boolean
  }
}

export interface StatsGridProps {
  kpis: KPIData[]
  isLoading?: boolean
}

export function StatsGrid({ kpis, isLoading = false }: StatsGridProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {kpis.map((kpi, index) => (
        <KPICard
          key={index}
          title={kpi.title}
          value={kpi.value}
          icon={kpi.icon}
          trend={kpi.trend}
          isLoading={isLoading}
        />
      ))}
    </div>
  )
}
