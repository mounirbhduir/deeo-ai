import {
  ResponsiveContainer,
  AreaChart as RechartsAreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts'
import { Card } from '@/components/common/Card'
import { Loader } from '@/components/common/Loader'

export interface AreaChartData {
  date: string
  count: number
}

export interface AreaChartProps {
  data: AreaChartData[]
  title: string
  height?: number
  isLoading?: boolean
}

export function AreaChart({
  data,
  title,
  height = 300,
  isLoading = false,
}: AreaChartProps) {
  return (
    <Card variant="bordered" padding="md">
      <h3 className="text-xl font-semibold mb-4 text-gray-800">{title}</h3>

      {isLoading ? (
        <div className="flex items-center justify-center" style={{ height }}>
          <Loader size="md" />
        </div>
      ) : data.length === 0 ? (
        <div
          className="flex items-center justify-center text-gray-500"
          style={{ height }}
        >
          Aucune donnée disponible
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={height}>
          <RechartsAreaChart data={data}>
            <defs>
              <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2563eb" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="date"
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
            />
            <YAxis stroke="#6b7280" style={{ fontSize: '12px' }} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #e5e7eb',
                borderRadius: '6px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              }}
            />
            <Legend
              wrapperStyle={{ fontSize: '14px', paddingTop: '10px' }}
            />
            <Area
              type="monotone"
              dataKey="count"
              stroke="#2563eb"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorCount)"
              name="Publications"
            />
          </RechartsAreaChart>
        </ResponsiveContainer>
      )}
    </Card>
  )
}
