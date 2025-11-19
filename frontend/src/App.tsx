import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Layout } from '@/components/layout/Layout'

// Pages
import Home from '@/pages/Home'
import Dashboard from '@/pages/Dashboard'
import { PublicationsSearch } from '@/pages/PublicationsSearch'
import { AuthorsList } from '@/pages/AuthorsList'
import { AuthorProfile } from '@/pages/AuthorProfile'
import { OrganisationsList } from '@/pages/OrganisationsList'
import { OrganisationProfile } from '@/pages/OrganisationProfile'
import { GraphsPage } from '@/pages/GraphsPage'
import ThemesPage from '@/pages/ThemesPage'
import ComponentsDemo from '@/pages/ComponentsDemo'
import NotFound from '@/pages/NotFound'

function App() {
  return (
    <Router>
      <Routes>
        {/* Routes avec Layout */}
        <Route path="/" element={<Layout><Home /></Layout>} />
        <Route path="/dashboard" element={<Layout><Dashboard /></Layout>} />
        <Route
          path="/publications/search"
          element={<Layout><PublicationsSearch /></Layout>}
        />
        <Route path="/authors" element={<Layout><AuthorsList /></Layout>} />
        <Route path="/authors/:id" element={<Layout><AuthorProfile /></Layout>} />
        <Route path="/graphs" element={<Layout><GraphsPage /></Layout>} />
        <Route path="/components" element={<Layout><ComponentsDemo /></Layout>} />

        {/* Routes futures (placeholders) */}
        <Route
          path="/publications/:id"
          element={<Layout><NotFound /></Layout>}
        />
        <Route path="/auteurs" element={<Layout><NotFound /></Layout>} />
        <Route path="/auteurs/:id" element={<Layout><NotFound /></Layout>} />
        <Route
          path="/organisations"
          element={<Layout><OrganisationsList /></Layout>}
        />
        <Route
          path="/organisations/:organisationId"
          element={<Layout><OrganisationProfile /></Layout>}
        />
        <Route path="/themes" element={<Layout><ThemesPage /></Layout>} />
        <Route path="/themes/:id" element={<Layout><NotFound /></Layout>} />
        <Route path="/about" element={<Layout><NotFound /></Layout>} />

        {/* 404 */}
        <Route path="*" element={<Layout><NotFound /></Layout>} />
      </Routes>
    </Router>
  )
}

export default App
