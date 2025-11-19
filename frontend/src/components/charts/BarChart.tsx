import {
  ResponsiveContainer,
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts'
import { Card } from '@/components/common/Card'
import { Loader } from '@/components/common/Loader'

export interface BarChartData {
  name: string
  value: number
}

export interface BarChartProps {
  data: BarChartData[]
  title: string
  height?: number
  isLoading?: boolean
}

export function BarChart({
  data,
  title,
  height = 300,
  isLoading = false,
}: BarChartProps) {
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
          <RechartsBarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="name"
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
              angle={-45}
              textAnchor="end"
              height={80}
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
            <Bar
              dataKey="value"
              fill="#2563eb"
              name="H-Index"
              radius={[4, 4, 0, 0]}
            />
          </RechartsBarChart>
        </ResponsiveContainer>
      )}
    </Card>
  )
}
