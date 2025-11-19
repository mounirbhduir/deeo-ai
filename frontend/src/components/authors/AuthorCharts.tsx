/**
 * AuthorCharts Component (Phase 4 - Step 6)
 *
 * Visualization suite for author statistics.
 * Displays 3 charts: Publications by Year, Publications by Theme, Citations by Year.
 */

import { useMemo } from 'react'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { Card } from '@/components/common/Card'
import type { AuthorStats } from '@/types/author'

interface AuthorChartsProps {
  statistics: AuthorStats
}

const COLORS = [
  '#4F46E5', // indigo-600
  '#7C3AED', // violet-600
  '#2563EB', // blue-600
  '#0891B2', // cyan-600
  '#059669', // emerald-600
  '#D97706', // amber-600
  '#DC2626', // red-600
  '#DB2777', // pink-600
]

export const AuthorCharts = ({ statistics }: AuthorChartsProps) => {
  // Transform publications by year for line chart
  const publicationsByYearData = useMemo(() => {
    return Object.entries(statistics.publications_by_year)
      .map(([year, count]) => ({
        year: parseInt(year),
        publications: count,
      }))
      .sort((a, b) => a.year - b.year)
  }, [statistics.publications_by_year])

  // Transform publications by theme for pie chart
  const publicationsByThemeData = useMemo(() => {
    return Object.entries(statistics.publications_by_theme)
      .map(([theme, count]) => ({
        name: theme,
        value: count,
      }))
      .sort((a, b) => b.value - a.value)
  }, [statistics.publications_by_theme])

  // Transform citations by year for line chart
  const citationsByYearData = useMemo(() => {
    return Object.entries(statistics.citations_by_year)
      .map(([year, count]) => ({
        year: parseInt(year),
        citations: count,
      }))
      .sort((a, b) => a.year - b.year)
  }, [statistics.citations_by_year])

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Publications by Year - Line Chart */}
      <Card className="col-span-1 lg:col-span-2">
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Publications Over Time
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={publicationsByYearData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="year"
                label={{ value: 'Year', position: 'insideBottom', offset: -5 }}
              />
              <YAxis
                label={{
                  value: 'Publications',
                  angle: -90,
                  position: 'insideLeft',
                }}
              />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="publications"
                stroke="#4F46E5"
                strokeWidth={2}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Publications by Theme - Pie Chart */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Publications by Theme
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={publicationsByThemeData}
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
                {publicationsByThemeData.map((_entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Citations by Year - Bar Chart */}
      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Citations Over Time
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={citationsByYearData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="citations" fill="#7C3AED" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  )
}
