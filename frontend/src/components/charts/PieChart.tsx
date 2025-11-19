import {
  ResponsiveContainer,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
} from 'recharts'
import { Card } from '@/components/common/Card'
import { Loader } from '@/components/common/Loader'

export interface PieChartData {
  name: string
  value: number
}

export interface PieChartProps {
  data: PieChartData[]
  title: string
  height?: number
  isLoading?: boolean
}

// Color palette for pie slices
const COLORS = ['#2563eb', '#4f46e5', '#7c3aed', '#c026d3', '#db2777']

export function PieChart({
  data,
  title,
  height = 300,
  isLoading = false,
}: PieChartProps) {
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
          <RechartsPieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) =>
                `${name}: ${(percent * 100).toFixed(0)}%`
              }
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {data.map((_, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[index % COLORS.length]}
                />
              ))}
            </Pie>
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
              iconType="circle"
            />
          </RechartsPieChart>
        </ResponsiveContainer>
      )}
    </Card>
  )
}
