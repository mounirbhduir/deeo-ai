import { useMemo } from 'react'
import { FileText, Users, Building2, TrendingUp } from 'lucide-react'
import { Breadcrumb } from '@/components/layout/Breadcrumb'
import { StatsGrid } from '@/components/dashboard/StatsGrid'
import { LineChart } from '@/components/charts/LineChart'
import { BarChart } from '@/components/charts/BarChart'
import { PieChart } from '@/components/charts/PieChart'
import { AreaChart } from '@/components/charts/AreaChart'
import { Alert } from '@/components/common/Alert'
import { useStatistics } from '@/hooks/useStatistics'
import { usePublications } from '@/hooks/usePublications'
import { useAuteurs } from '@/hooks/useAuteurs'
import { useThemes } from '@/hooks/useThemes'
import type { Publication, Auteur, Theme } from '@/types/api'

export default function Dashboard() {
  // Fetch data from API
  const { data: stats, isLoading: statsLoading, isError: statsError } = useStatistics()
  const { data: publicationsData, isLoading: pubsLoading } = usePublications({
    page_size: 100,
    sort: '-date_publication',
  })
  const { data: auteurs, isLoading: auteursLoading } = useAuteurs({
    sort: '-h_index',
    limit: 10,
  })
  const { data: themes, isLoading: themesLoading } = useThemes({
    sort: '-nombre_publications',
    limit: 5,
  })

  // Prepare KPIs data
  const kpis = useMemo(
    () => [
      {
        title: 'Publications totales',
        value: stats?.total_publications || 0,
        icon: <FileText className="w-6 h-6" />,
        trend: { value: 12.5, isPositive: true },
      },
      {
        title: 'Auteurs totaux',
        value: stats?.total_auteurs || 0,
        icon: <Users className="w-6 h-6" />,
        trend: { value: 8.3, isPositive: true },
      },
      {
        title: 'Organisations totales',
        value: stats?.total_organisations || 0,
        icon: <Building2 className="w-6 h-6" />,
        trend: { value: 5.1, isPositive: true },
      },
      {
        title: 'Publications récentes',
        value: stats?.publications_last_7_days || 0,
        icon: <TrendingUp className="w-6 h-6" />,
        trend: { value: 15.7, isPositive: true },
      },
    ],
    [stats]
  )

  // Prepare Line Chart data (publications by month - last 12 months)
  const lineChartData = useMemo(() => {
    return prepareLineChartData(publicationsData?.items || [])
  }, [publicationsData])

  // Prepare Bar Chart data (top 10 authors by h-index)
  const barChartData = useMemo(() => {
    return prepareBarChartData(auteurs || [])
  }, [auteurs])

  // Prepare Pie Chart data (top 5 themes)
  const pieChartData = useMemo(() => {
    return preparePieChartData(themes || [])
  }, [themes])

  // Prepare Area Chart data (temporal trends)
  const areaChartData = useMemo(() => {
    return prepareAreaChartData(publicationsData?.items || [])
  }, [publicationsData])

  return (
    <div>
      <Breadcrumb />

      <div className="p-6 space-y-6">
        {/* Page Title */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Tableau de bord</h1>
          <p className="text-gray-600 mt-2">
            Vue d&apos;ensemble de l&apos;observatoire DEEO.AI
          </p>
        </div>

        {/* Error Alert */}
        {statsError && (
          <Alert variant="error" title="Erreur de chargement">
            Impossible de récupérer les statistiques. Vérifiez que le backend
            est démarré.
          </Alert>
        )}

        {/* KPIs Grid */}
        <StatsGrid kpis={kpis} isLoading={statsLoading} />

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <LineChart
            title="Évolution Publications (12 derniers mois)"
            data={lineChartData}
            isLoading={pubsLoading}
          />
          <BarChart
            title="Top 10 Auteurs (H-Index)"
            data={barChartData}
            isLoading={auteursLoading}
          />
          <PieChart
            title="Distribution Thèmes (Top 5)"
            data={pieChartData}
            isLoading={themesLoading}
          />
          <AreaChart
            title="Tendances Temporelles"
            data={areaChartData}
            isLoading={pubsLoading}
          />
        </div>
      </div>
    </div>
  )
}

// Helper Functions

/**
 * Prepare data for Line Chart (publications by month - last 12 months)
 */
function prepareLineChartData(publications: Publication[]) {
  const now = new Date()
  const monthsMap = new Map<string, number>()

  // Initialize last 12 months with 0
  for (let i = 11; i >= 0; i--) {
    const date = new Date(now.getFullYear(), now.getMonth() - i, 1)
    const monthKey = date.toLocaleString('fr-FR', { month: 'short', year: 'numeric' })
    monthsMap.set(monthKey, 0)
  }

  // Count publications per month
  publications.forEach((pub) => {
    const pubDate = new Date(pub.date_publication)
    const monthKey = pubDate.toLocaleString('fr-FR', { month: 'short', year: 'numeric' })
    if (monthsMap.has(monthKey)) {
      monthsMap.set(monthKey, (monthsMap.get(monthKey) || 0) + 1)
    }
  })

  return Array.from(monthsMap.entries()).map(([month, count]) => ({
    month,
    count,
  }))
}

/**
 * Prepare data for Bar Chart (top authors by h-index)
 */
function prepareBarChartData(auteurs: Auteur[]) {
  return auteurs.slice(0, 10).map((auteur) => ({
    name: `${auteur.prenom} ${auteur.nom}`.substring(0, 20),
    value: auteur.h_index,
  }))
}

/**
 * Prepare data for Pie Chart (top themes by publication count)
 */
function preparePieChartData(themes: Theme[]) {
  return themes.slice(0, 5).map((theme) => ({
    name: theme.label.substring(0, 30),
    value: theme.nombre_publications,
  }))
}

/**
 * Prepare data for Area Chart (temporal trends - last 6 months)
 */
function prepareAreaChartData(publications: Publication[]) {
  const now = new Date()
  const monthsMap = new Map<string, number>()

  // Initialize last 6 months with 0
  for (let i = 5; i >= 0; i--) {
    const date = new Date(now.getFullYear(), now.getMonth() - i, 1)
    const monthKey = date.toLocaleString('fr-FR', { month: 'short' })
    monthsMap.set(monthKey, 0)
  }

  // Count publications per month
  publications.forEach((pub) => {
    const pubDate = new Date(pub.date_publication)
    const diffMonths =
      (now.getFullYear() - pubDate.getFullYear()) * 12 +
      (now.getMonth() - pubDate.getMonth())

    if (diffMonths >= 0 && diffMonths <= 5) {
      const monthKey = pubDate.toLocaleString('fr-FR', { month: 'short' })
      if (monthsMap.has(monthKey)) {
        monthsMap.set(monthKey, (monthsMap.get(monthKey) || 0) + 1)
      }
    }
  })

  return Array.from(monthsMap.entries()).map(([date, count]) => ({
    date,
    count,
  }))
}
