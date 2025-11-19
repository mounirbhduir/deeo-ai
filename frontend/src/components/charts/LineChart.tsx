import {
  ResponsiveContainer,
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts'
import { Card } from '@/components/common/Card'
import { Loader } from '@/components/common/Loader'

export interface LineChartData {
  month: string
  count: number
}

export interface LineChartProps {
  data: LineChartData[]
  title: string
  height?: number
  isLoading?: boolean
}

export function LineChart({
  data,
  title,
  height = 300,
  isLoading = false,
}: LineChartProps) {
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
          <RechartsLineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="month"
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
            <Line
              type="monotone"
              dataKey="count"
              stroke="#2563eb"
              strokeWidth={2}
              dot={{ fill: '#2563eb', r: 4 }}
              activeDot={{ r: 6 }}
              name="Publications"
            />
          </RechartsLineChart>
        </ResponsiveContainer>
      )}
    </Card>
  )
}
