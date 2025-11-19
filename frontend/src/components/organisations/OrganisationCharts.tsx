import { useMemo } from 'react'
import { LineChart, Line, PieChart, Pie, BarChart, Bar, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Card } from '@/components/common/Card'
import type { OrganisationStats } from '@/types/organisation'

const COLORS = ['#4F46E5', '#7C3AED', '#2563EB', '#0891B2', '#059669', '#D97706', '#DC2626', '#DB2777']

export const OrganisationCharts = ({ statistics }: { statistics: OrganisationStats }) => {
  const publicationsByYearData = useMemo(() => {
    return Object.entries(statistics.publications_by_year)
      .map(([year, count]) => ({ year: parseInt(year), publications: count }))
      .sort((a, b) => a.year - b.year)
  }, [statistics.publications_by_year])

  const publicationsByThemeData = useMemo(() => {
    return Object.entries(statistics.publications_by_theme)
      .map(([theme, count]) => ({ name: theme, value: count }))
      .sort((a, b) => b.value - a.value)
  }, [statistics.publications_by_theme])

  const topAuthorsData = useMemo(() => {
    return statistics.top_authors.slice(0, 10).map(a => ({
      name: `${a.prenom} ${a.nom}`,
      h_index: a.h_index
    }))
  }, [statistics.top_authors])

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Card className="col-span-1 lg:col-span-2">
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Publications Over Time</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={publicationsByYearData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="publications" stroke="#4F46E5" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Publications by Theme</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={publicationsByThemeData} cx="50%" cy="50%" labelLine={false} label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`} outerRadius={80} fill="#8884d8" dataKey="value">
                {publicationsByThemeData.map((_entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card>
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Researchers (h-index)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={topAuthorsData} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="name" type="category" width={100} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="h_index" fill="#7C3AED" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  )
}
