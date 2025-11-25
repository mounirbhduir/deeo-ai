# PROMPT CLAUDE CODE - PHASE 4 ÉTAPE 2 : ARCHITECTURE DE BASE

**Date** : 18 Novembre 2025  
**Projet** : DEEO.AI - AI Dynamic Emergence and Evolution Observatory  
**Phase** : 4/5 - Frontend React & Analytics  
**Étape** : 2/10 - Architecture de Base (Layout, Router, Navigation)  
**Durée estimée** : 1-2h

---

## 🌟 VISION & MOTIVATION

**DEEO.AI** est une plateforme open-source d'observatoire IA destinée à devenir une référence mondiale pour chercheurs, entreprises, institutions et décideurs.

**Vous contribuez à** :
- Créer une interface utilisateur moderne et intuitive
- Rendre l'exploration des publications IA fluide et agréable
- Poser les bases d'une navigation professionnelle
- Construire une architecture scalable pour les prochaines étapes

**Excellence is your standard. Quality is your commitment. Impact is your goal.** 🚀

---

## 📊 CONTEXTE PROJET

### Étapes Complétées

**✅ Étape 1/10** : Setup Projet (COMPLÉTÉ)
- React 18 + TypeScript + Vite configuré
- Tailwind CSS + TanStack Query setup
- Structure dossiers créée
- 23 fichiers, 0 erreurs, bundle ~60 KB
- Frontend opérationnel : http://localhost:5173
- Backend opérationnel : http://localhost:8000/api/v1

### État Actuel

**Frontend** : Infrastructure technique prête  
**Backend** : API REST opérationnelle (416/416 tests passing)

**Répertoire de travail** :
```
C:\Users\user\deeo-ai-workspace\deeo-ai-poc\frontend\
```

---

## 🎯 OBJECTIFS ÉTAPE 2

### Objectif Principal

Créer l'architecture de base de l'application : Layout responsive, React Router avec routes principales, navigation fluide, et pages de base (Home, Dashboard, Search).

### Objectifs Spécifiques

1. **Créer composants Layout** :
   - Header (avec navigation principale)
   - Sidebar (navigation secondaire, collapsible)
   - Footer (liens, copyright)
   - Layout wrapper (combine Header + Sidebar + Content + Footer)

2. **Configurer React Router** :
   - Routes principales (/, /dashboard, /publications/search, etc.)
   - Navigation programmatique
   - Route guards (préparation future auth)

3. **Implémenter Navigation** :
   - Navigation responsive (mobile/desktop)
   - Menu burger pour mobile
   - Active states sur liens
   - Breadcrumb (fil d'Ariane)

4. **Créer Pages de Base** :
   - Home (landing page avec hero section)
   - Dashboard (skeleton avec message "Coming soon")
   - SearchPublications (skeleton avec barre recherche)
   - NotFound (404 page)

5. **Tester Connexion API** :
   - Créer un composant HealthCheck
   - Vérifier que TanStack Query fonctionne
   - Afficher statut API dans Footer

---

## 📁 FICHIERS À CRÉER

### Structure Cible

```
src/
├── components/
│   ├── layout/
│   │   ├── Header.tsx              # NEW - Header principal
│   │   ├── Sidebar.tsx             # NEW - Sidebar navigation
│   │   ├── Footer.tsx              # NEW - Footer
│   │   ├── Layout.tsx              # NEW - Layout wrapper
│   │   └── Breadcrumb.tsx          # NEW - Fil d'Ariane
│   └── common/
│       ├── Button.tsx              # NEW - Composant Button réutilisable
│       ├── Logo.tsx                # NEW - Logo DEEO.AI
│       └── HealthCheck.tsx         # NEW - Vérification API
│
├── pages/
│   ├── Home.tsx                    # NEW - Page d'accueil
│   ├── Dashboard.tsx               # NEW - Dashboard (skeleton)
│   ├── SearchPublications.tsx     # NEW - Recherche (skeleton)
│   └── NotFound.tsx                # NEW - Page 404
│
├── hooks/
│   └── useHealth.ts                # NEW - Hook pour health check API
│
└── App.tsx                         # MODIFIER - Ajouter Router et Layout
```

**Total** : 12 nouveaux fichiers + 1 modification

---

## 🔧 SPÉCIFICATIONS TECHNIQUES

### 1. Composant Header

**`src/components/layout/Header.tsx`**

**Fonctionnalités** :
- Logo DEEO.AI cliquable (retour à home)
- Navigation principale (Desktop) : Home | Dashboard | Search | Themes
- Menu burger (Mobile)
- Search bar (optionnel pour cette étape)

**Design** :
- Fond blanc avec ombre légère
- Sticky top
- Height : 64px (desktop), 56px (mobile)
- Padding horizontal : responsive

**Code** :
```tsx
import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Menu, X, Search } from 'lucide-react'
import { Logo } from '@/components/common/Logo'
import { Button } from '@/components/common/Button'

const navItems = [
  { name: 'Accueil', path: '/' },
  { name: 'Dashboard', path: '/dashboard' },
  { name: 'Recherche', path: '/publications/search' },
  { name: 'Thèmes', path: '/themes' },
]

export function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const location = useLocation()

  const isActive = (path: string) => location.pathname === path

  return (
    <header className="sticky top-0 z-50 bg-white border-b border-gray-200 shadow-sm">
      <div className="container-custom">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <Logo />
            <span className="text-xl font-bold text-gray-900">
              DEEO.AI
            </span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`text-sm font-medium transition-colors ${
                  isActive(item.path)
                    ? 'text-primary-600'
                    : 'text-gray-700 hover:text-primary-600'
                }`}
              >
                {item.name}
              </Link>
            ))}
          </nav>

          {/* Actions */}
          <div className="hidden md:flex items-center space-x-4">
            <Button variant="ghost" size="sm">
              <Search className="h-4 w-4" />
            </Button>
          </div>

          {/* Mobile Menu Button */}
          <button
            type="button"
            className="md:hidden p-2 rounded-md text-gray-700 hover:bg-gray-100"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? (
              <X className="h-6 w-6" />
            ) : (
              <Menu className="h-6 w-6" />
            )}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-gray-200 bg-white">
          <nav className="container-custom py-4 space-y-2">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`block px-4 py-2 rounded-md text-base font-medium ${
                  isActive(item.path)
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
                onClick={() => setMobileMenuOpen(false)}
              >
                {item.name}
              </Link>
            ))}
          </nav>
        </div>
      )}
    </header>
  )
}
```

---

### 2. Composant Sidebar

**`src/components/layout/Sidebar.tsx`**

**Fonctionnalités** :
- Navigation secondaire (sections)
- Collapsible (peut se réduire)
- Icônes + labels
- Active state

**Design** :
- Largeur : 256px (expanded), 64px (collapsed)
- Fond : gris léger
- Border right

**Code** :
```tsx
import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  FileText,
  Users,
  Building2,
  Tags,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react'

const sidebarItems = [
  { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  { name: 'Publications', path: '/publications/search', icon: FileText },
  { name: 'Auteurs', path: '/auteurs', icon: Users },
  { name: 'Organisations', path: '/organisations', icon: Building2 },
  { name: 'Thèmes', path: '/themes', icon: Tags },
]

interface SidebarProps {
  collapsed?: boolean
}

export function Sidebar({ collapsed: initialCollapsed = false }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(initialCollapsed)
  const location = useLocation()

  const isActive = (path: string) => location.pathname.startsWith(path)

  return (
    <aside
      className={`hidden lg:flex flex-col bg-gray-50 border-r border-gray-200 transition-all duration-300 ${
        collapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Collapse Toggle */}
      <div className="flex items-center justify-end p-4 border-b border-gray-200">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-2 rounded-md hover:bg-gray-200 transition-colors"
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? (
            <ChevronRight className="h-5 w-5 text-gray-600" />
          ) : (
            <ChevronLeft className="h-5 w-5 text-gray-600" />
          )}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {sidebarItems.map((item) => {
          const Icon = item.icon
          const active = isActive(item.path)

          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                active
                  ? 'bg-primary-100 text-primary-700'
                  : 'text-gray-700 hover:bg-gray-200'
              }`}
              title={collapsed ? item.name : undefined}
            >
              <Icon className="h-5 w-5 flex-shrink-0" />
              {!collapsed && <span className="ml-3">{item.name}</span>}
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
```

---

### 3. Composant Footer

**`src/components/layout/Footer.tsx`**

**Fonctionnalités** :
- Liens utiles (Docs, GitHub, About)
- Copyright
- HealthCheck status (mini badge)

**Code** :
```tsx
import { Link } from 'react-router-dom'
import { Github, FileText, Info } from 'lucide-react'
import { HealthCheck } from '@/components/common/HealthCheck'

export function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="container-custom py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* About */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-4">
              DEEO.AI
            </h3>
            <p className="text-sm text-gray-600">
              AI Dynamic Emergence and Evolution Observatory - Plateforme
              open-source de tracking des publications IA.
            </p>
          </div>

          {/* Links */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-4">
              Liens
            </h3>
            <ul className="space-y-2">
              <li>
                <a
                  href="https://github.com/your-repo/deeo-ai"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-gray-600 hover:text-primary-600 flex items-center"
                >
                  <Github className="h-4 w-4 mr-2" />
                  GitHub
                </a>
              </li>
              <li>
                <a
                  href="http://localhost:8000/docs"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-gray-600 hover:text-primary-600 flex items-center"
                >
                  <FileText className="h-4 w-4 mr-2" />
                  API Docs
                </a>
              </li>
              <li>
                <Link
                  to="/about"
                  className="text-sm text-gray-600 hover:text-primary-600 flex items-center"
                >
                  <Info className="h-4 w-4 mr-2" />
                  À propos
                </Link>
              </li>
            </ul>
          </div>

          {/* Status */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-4">
              Statut API
            </h3>
            <HealthCheck />
          </div>
        </div>

        {/* Copyright */}
        <div className="mt-8 pt-8 border-t border-gray-200">
          <p className="text-sm text-gray-600 text-center">
            © {currentYear} DEEO.AI - Master Big Data & AI - UIR
          </p>
        </div>
      </div>
    </footer>
  )
}
```

---

### 4. Composant Layout

**`src/components/layout/Layout.tsx`**

**Fonctionnalités** :
- Wrapper principal
- Combine Header + Sidebar + Content + Footer
- Gère layout responsive

**Code** :
```tsx
import { ReactNode } from 'react'
import { Header } from './Header'
import { Sidebar } from './Sidebar'
import { Footer } from './Footer'

interface LayoutProps {
  children: ReactNode
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 bg-gray-50">
          <div className="container-custom py-8">{children}</div>
        </main>
      </div>
      <Footer />
    </div>
  )
}
```

---

### 5. Composant Button

**`src/components/common/Button.tsx`**

Composant Button réutilisable avec variants.

**Code** :
```tsx
import { ButtonHTMLAttributes, ReactNode } from 'react'
import clsx from 'clsx'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode
  variant?: 'primary' | 'secondary' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
}

export function Button({
  children,
  variant = 'primary',
  size = 'md',
  className,
  ...props
}: ButtonProps) {
  return (
    <button
      className={clsx(
        'inline-flex items-center justify-center font-medium rounded-md transition-colors',
        'focus:outline-none focus:ring-2 focus:ring-offset-2',
        {
          // Variants
          'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500':
            variant === 'primary',
          'bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500':
            variant === 'secondary',
          'bg-transparent text-gray-700 hover:bg-gray-100 focus:ring-gray-500':
            variant === 'ghost',
          // Sizes
          'px-3 py-1.5 text-sm': size === 'sm',
          'px-4 py-2 text-base': size === 'md',
          'px-6 py-3 text-lg': size === 'lg',
        },
        className
      )}
      {...props}
    >
      {children}
    </button>
  )
}
```

---

### 6. Composant Logo

**`src/components/common/Logo.tsx`**

Logo simple DEEO.AI (SVG ou texte stylisé).

**Code** :
```tsx
export function Logo() {
  return (
    <svg
      className="h-8 w-8"
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <rect width="32" height="32" rx="8" fill="url(#gradient)" />
      <path
        d="M8 12h16M8 16h16M8 20h12"
        stroke="white"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <defs>
        <linearGradient
          id="gradient"
          x1="0"
          y1="0"
          x2="32"
          y2="32"
          gradientUnits="userSpaceOnUse"
        >
          <stop stopColor="#3B82F6" />
          <stop offset="1" stopColor="#6366F1" />
        </linearGradient>
      </defs>
    </svg>
  )
}
```

---

### 7. Composant HealthCheck

**`src/components/common/HealthCheck.tsx`**

Affiche le statut de l'API backend.

**Code** :
```tsx
import { useHealth } from '@/hooks/useHealth'

export function HealthCheck() {
  const { data, isLoading, error } = useHealth()

  if (isLoading) {
    return (
      <div className="flex items-center space-x-2">
        <div className="h-2 w-2 bg-gray-400 rounded-full animate-pulse" />
        <span className="text-sm text-gray-600">Vérification...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center space-x-2">
        <div className="h-2 w-2 bg-red-500 rounded-full" />
        <span className="text-sm text-red-600">API indisponible</span>
      </div>
    )
  }

  const isHealthy = data?.status === 'healthy'

  return (
    <div className="flex items-center space-x-2">
      <div
        className={`h-2 w-2 rounded-full ${
          isHealthy ? 'bg-green-500' : 'bg-yellow-500'
        }`}
      />
      <span
        className={`text-sm ${
          isHealthy ? 'text-green-600' : 'text-yellow-600'
        }`}
      >
        {isHealthy ? 'API opérationnelle' : 'API dégradée'}
      </span>
    </div>
  )
}
```

---

### 8. Composant Breadcrumb

**`src/components/layout/Breadcrumb.tsx`**

Fil d'Ariane pour navigation hiérarchique.

**Code** :
```tsx
import { Link, useLocation } from 'react-router-dom'
import { ChevronRight, Home } from 'lucide-react'

const routeLabels: Record<string, string> = {
  dashboard: 'Dashboard',
  publications: 'Publications',
  search: 'Recherche',
  auteurs: 'Auteurs',
  organisations: 'Organisations',
  themes: 'Thèmes',
}

export function Breadcrumb() {
  const location = useLocation()
  const pathSegments = location.pathname.split('/').filter(Boolean)

  if (pathSegments.length === 0) {
    return null
  }

  return (
    <nav className="flex items-center space-x-2 text-sm text-gray-600 mb-6">
      <Link to="/" className="hover:text-primary-600 flex items-center">
        <Home className="h-4 w-4" />
      </Link>

      {pathSegments.map((segment, index) => {
        const path = `/${pathSegments.slice(0, index + 1).join('/')}`
        const label = routeLabels[segment] || segment
        const isLast = index === pathSegments.length - 1

        return (
          <div key={path} className="flex items-center space-x-2">
            <ChevronRight className="h-4 w-4 text-gray-400" />
            {isLast ? (
              <span className="font-medium text-gray-900 capitalize">
                {label}
              </span>
            ) : (
              <Link to={path} className="hover:text-primary-600 capitalize">
                {label}
              </Link>
            )}
          </div>
        )
      })}
    </nav>
  )
}
```

---

### 9. Hook useHealth

**`src/hooks/useHealth.ts`**

Hook TanStack Query pour vérifier le statut de l'API.

**Code** :
```ts
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/api/client'

interface HealthResponse {
  status: string
  api: string
  database: string
  cache: string
}

async function fetchHealth(): Promise<HealthResponse> {
  const response = await apiClient.get('/health')
  return response.data
}

export function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
    refetchInterval: 30000, // Refetch every 30 seconds
    staleTime: 10000, // Consider stale after 10 seconds
  })
}
```

---

### 10. Page Home

**`src/pages/Home.tsx`**

Landing page avec hero section.

**Code** :
```tsx
import { Link } from 'react-router-dom'
import { ArrowRight, Database, TrendingUp, Users } from 'lucide-react'
import { Button } from '@/components/common/Button'

export default function Home() {
  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <section className="text-center py-20">
        <h1 className="text-5xl md:text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600 mb-6">
          DEEO.AI
        </h1>
        <p className="text-xl md:text-2xl text-gray-700 mb-4">
          AI Dynamic Emergence and Evolution Observatory
        </p>
        <p className="text-lg text-gray-600 max-w-3xl mx-auto mb-8">
          Explorez l'écosystème des publications scientifiques en Intelligence
          Artificielle. Suivez les tendances, découvrez les chercheurs
          influents, et restez à jour avec les dernières avancées.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link to="/dashboard">
            <Button size="lg">
              Accéder au Dashboard
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
          <Link to="/publications/search">
            <Button variant="secondary" size="lg">
              Rechercher des Publications
            </Button>
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="bg-white p-8 rounded-lg shadow-md">
          <Database className="h-12 w-12 text-blue-600 mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            15,000+ Publications
          </h3>
          <p className="text-gray-600">
            Base de données complète de publications scientifiques en IA
            collectées depuis arXiv.
          </p>
        </div>

        <div className="bg-white p-8 rounded-lg shadow-md">
          <TrendingUp className="h-12 w-12 text-indigo-600 mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Analyse ML Automatique
          </h3>
          <p className="text-gray-600">
            Classification automatique par thèmes grâce au Machine Learning
            (BART zero-shot).
          </p>
        </div>

        <div className="bg-white p-8 rounded-lg shadow-md">
          <Users className="h-12 w-12 text-purple-600 mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            10,000+ Chercheurs
          </h3>
          <p className="text-gray-600">
            Profils détaillés des auteurs avec h-index, affiliations et
            collaborations.
          </p>
        </div>
      </section>
    </div>
  )
}
```

---

### 11. Page Dashboard

**`src/pages/Dashboard.tsx`**

Skeleton pour le dashboard (sera complété à l'Étape 4).

**Code** :
```tsx
import { Breadcrumb } from '@/components/layout/Breadcrumb'

export default function Dashboard() {
  return (
    <div>
      <Breadcrumb />
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Dashboard
        </h1>
        <p className="text-gray-600 mb-8">
          Les statistiques et graphiques seront disponibles à l'Étape 4.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-32 bg-gray-100 rounded-lg animate-pulse"
            />
          ))}
        </div>
      </div>
    </div>
  )
}
```

---

### 12. Page SearchPublications

**`src/pages/SearchPublications.tsx`**

Skeleton pour la recherche (sera complété à l'Étape 5).

**Code** :
```tsx
import { Search } from 'lucide-react'
import { Breadcrumb } from '@/components/layout/Breadcrumb'

export default function SearchPublications() {
  return (
    <div>
      <Breadcrumb />
      <div className="bg-white rounded-lg shadow-md p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Recherche de Publications
        </h1>
        <div className="relative mb-8">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Rechercher par titre, auteur, thème..."
            className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            disabled
          />
        </div>
        <p className="text-gray-600 text-center">
          La fonctionnalité de recherche avancée sera disponible à l'Étape 5.
        </p>
      </div>
    </div>
  )
}
```

---

### 13. Page NotFound

**`src/pages/NotFound.tsx`**

Page 404 avec lien retour.

**Code** :
```tsx
import { Link } from 'react-router-dom'
import { Home } from 'lucide-react'
import { Button } from '@/components/common/Button'

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
      <h1 className="text-9xl font-bold text-gray-200 mb-4">404</h1>
      <h2 className="text-3xl font-semibold text-gray-900 mb-4">
        Page non trouvée
      </h2>
      <p className="text-lg text-gray-600 mb-8 max-w-md">
        La page que vous recherchez n'existe pas ou a été déplacée.
      </p>
      <Link to="/">
        <Button>
          <Home className="mr-2 h-5 w-5" />
          Retour à l'accueil
        </Button>
      </Link>
    </div>
  )
}
```

---

### 14. Modification App.tsx

**`src/App.tsx`** (MODIFIER)

Intégrer React Router avec Layout.

**Code complet** :
```tsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Layout } from '@/components/layout/Layout'

// Pages
import Home from '@/pages/Home'
import Dashboard from '@/pages/Dashboard'
import SearchPublications from '@/pages/SearchPublications'
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
          element={<Layout><SearchPublications /></Layout>}
        />
        
        {/* Routes futures (placeholders) */}
        <Route
          path="/publications/:id"
          element={<Layout><NotFound /></Layout>}
        />
        <Route path="/auteurs" element={<Layout><NotFound /></Layout>} />
        <Route path="/auteurs/:id" element={<Layout><NotFound /></Layout>} />
        <Route
          path="/organisations"
          element={<Layout><NotFound /></Layout>}
        />
        <Route
          path="/organisations/:id"
          element={<Layout><NotFound /></Layout>}
        />
        <Route path="/themes" element={<Layout><NotFound /></Layout>} />
        <Route path="/themes/:id" element={<Layout><NotFound /></Layout>} />

        {/* 404 */}
        <Route path="*" element={<Layout><NotFound /></Layout>} />
      </Routes>
    </Router>
  )
}

export default App
```

---

### 15. Mise à Jour API Client

**`src/api/client.ts`** (MODIFIER - ajouter baseURL correcte)

Corriger l'URL de base pour pointer vers `/api/v1` :

```ts
import axios from 'axios'
import { API_BASE_URL } from '@/config/constants'

export const apiClient = axios.create({
  baseURL: API_BASE_URL, // Déjà défini dans constants.ts
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)
```

Vérifier que `src/config/constants.ts` contient bien :
```ts
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
```

Et que `.env.local` contient :
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

## ✅ CRITÈRES DE SUCCÈS

### Fonctionnels

- [ ] Header affiché avec navigation fonctionnelle
- [ ] Sidebar affichée (desktop) avec icônes
- [ ] Footer affiché avec liens et HealthCheck
- [ ] Navigation entre pages fonctionne (Home, Dashboard, Search)
- [ ] Menu burger fonctionne (mobile)
- [ ] Active states sur liens de navigation
- [ ] Breadcrumb affiché sur pages internes
- [ ] HealthCheck affiche statut API (vert = healthy)
- [ ] Page 404 accessible via URL inexistante

### Techniques

- [ ] `npm run dev` démarre sans erreur
- [ ] `npm run build` compile sans erreur
- [ ] `npm run lint` 0 errors, 0 warnings
- [ ] `npm run type-check` 0 TypeScript errors
- [ ] TanStack Query fonctionne (useHealth hook)
- [ ] Routes React Router toutes configurées

### Qualité

- [ ] Components réutilisables (Button, Logo)
- [ ] Types TypeScript complets (props interfaces)
- [ ] Responsive mobile/tablet/desktop
- [ ] Accessibilité (aria-labels, keyboard navigation)
- [ ] Code formaté Prettier
- [ ] Pas de console errors dans browser

### UI/UX

- [ ] Design cohérent (Tailwind classes)
- [ ] Transitions fluides
- [ ] Loading states appropriés
- [ ] Hover states sur boutons/liens
- [ ] Layout responsive sans scroll horizontal

---

## 🚀 INSTRUCTIONS D'EXÉCUTION

### Étape 1 : Créer Composants Layout

Dans l'ordre :
1. `src/components/common/Logo.tsx`
2. `src/components/common/Button.tsx`
3. `src/components/common/HealthCheck.tsx`
4. `src/hooks/useHealth.ts`
5. `src/components/layout/Header.tsx`
6. `src/components/layout/Sidebar.tsx`
7. `src/components/layout/Footer.tsx`
8. `src/components/layout/Breadcrumb.tsx`
9. `src/components/layout/Layout.tsx`

### Étape 2 : Créer Pages

10. `src/pages/Home.tsx`
11. `src/pages/Dashboard.tsx`
12. `src/pages/SearchPublications.tsx`
13. `src/pages/NotFound.tsx`

### Étape 3 : Modifier App.tsx

14. Remplacer contenu de `src/App.tsx` avec Router + Layout

### Étape 4 : Vérifier Configuration

15. Vérifier `src/api/client.ts` (baseURL correcte)
16. Vérifier `.env.local` (VITE_API_BASE_URL définie)

### Étape 5 : Tester

```bash
cd frontend
npm run dev
```

**Vérifier** :
- http://localhost:5173/ → Home page avec hero section
- http://localhost:5173/dashboard → Dashboard skeleton
- http://localhost:5173/publications/search → Search skeleton
- http://localhost:5173/invalid-route → Page 404

**Vérifier Header** :
- Logo cliquable (retour home)
- Navigation desktop (4 liens)
- Menu burger mobile (responsive)
- Active states (lien actif en bleu)

**Vérifier Sidebar** (desktop uniquement) :
- 5 liens avec icônes
- Bouton collapse fonctionne
- Active states

**Vérifier Footer** :
- Liens affichés
- HealthCheck badge vert (si API UP)

### Étape 6 : Tester Responsive

Ouvrir DevTools → Toggle device toolbar :
- Mobile (375px) : Menu burger, pas de sidebar
- Tablet (768px) : Navigation desktop, pas de sidebar
- Desktop (1024px+) : Navigation desktop + sidebar

### Étape 7 : Valider Qualité

```bash
npm run lint
npm run type-check
npm run build
```

Tous doivent passer sans erreur.

---

## 📋 FORMAT DE RAPPORT

```markdown
# RAPPORT - PHASE 4 ÉTAPE 2 : ARCHITECTURE DE BASE

## Statut : ✅ SUCCÈS / ❌ ÉCHEC PARTIEL / ⚠️ PROBLÈMES

## Réalisations

- [x] Composants Layout créés (Header, Sidebar, Footer, Layout, Breadcrumb)
- [x] Composants communs créés (Button, Logo, HealthCheck)
- [x] Hook useHealth créé et fonctionnel
- [x] Pages créées (Home, Dashboard, Search, NotFound)
- [x] React Router configuré avec toutes routes
- [x] Navigation fonctionnelle (desktop + mobile)
- [x] Responsive design validé
- [x] HealthCheck affiche statut API

## Fichiers Créés/Modifiés

| Fichier | Chemin | Lignes | Rôle |
|---------|--------|--------|------|
| Header.tsx | src/components/layout/ | XX | Header + nav |
| Sidebar.tsx | src/components/layout/ | XX | Sidebar navigation |
| Footer.tsx | src/components/layout/ | XX | Footer + links |
| Layout.tsx | src/components/layout/ | XX | Layout wrapper |
| Breadcrumb.tsx | src/components/layout/ | XX | Fil d'Ariane |
| Button.tsx | src/components/common/ | XX | Composant Button |
| Logo.tsx | src/components/common/ | XX | Logo SVG |
| HealthCheck.tsx | src/components/common/ | XX | API status |
| useHealth.ts | src/hooks/ | XX | Hook TanStack Query |
| Home.tsx | src/pages/ | XX | Landing page |
| Dashboard.tsx | src/pages/ | XX | Dashboard skeleton |
| SearchPublications.tsx | src/pages/ | XX | Search skeleton |
| NotFound.tsx | src/pages/ | XX | 404 page |
| App.tsx | src/ | XX | Router + Layout (MODIFIÉ) |

**Total** : 13 nouveaux fichiers + 1 modifié, ~XXX lignes de code

## Tests de Validation

### Fonctionnel
✅ Navigation fonctionne entre pages
✅ Menu burger mobile opérationnel
✅ Sidebar collapsible (desktop)
✅ HealthCheck affiche statut API
✅ Breadcrumb affiché correctement
✅ Active states sur navigation

### Responsive
✅ Mobile (375px) : Menu burger, layout adapté
✅ Tablet (768px) : Nav desktop, pas de sidebar
✅ Desktop (1024px+) : Nav desktop + sidebar

### Qualité Code
```bash
npm run lint
✅ 0 errors, 0 warnings

npm run type-check
✅ 0 TypeScript errors

npm run build
✅ Compile sans erreur (XX secondes)
```

## Captures d'Écran

[Optionnel : Screenshots de Home, Dashboard, Mobile menu]

## Métriques

- **Nouveaux composants** : 13
- **Lignes de code ajoutées** : ~XXX
- **Routes configurées** : 10
- **Bundle size** : XX KB (vs XX KB étape 1)
- **Temps build** : XX secondes

## Problèmes Rencontrés

[Si aucun : "Aucun problème rencontré."]

[Si problèmes : Lister avec résolutions]

## API Backend

✅ Backend accessible : http://localhost:8000/api/v1
✅ Health endpoint : http://localhost:8000/api/health
✅ HealthCheck badge affiche statut : Vert (healthy)

## Prochaine Étape

**Étape 3/10** : Composants Communs (Input, Select, Card, Loader, Pagination)

**Préparation nécessaire** :
- Architecture de base validée ✅
- Backend API opérationnel ✅

## Notes

[Remarques additionnelles, améliorations possibles]

---

**Généré le** : [Date]  
**Durée effective** : [Temps]  
**Par** : Claude Code
```

---

## 📞 SUPPORT

### Problèmes Courants

**1. HealthCheck badge rouge (API indisponible)** :
```bash
# Vérifier backend
cd C:\Users\user\deeo-ai-workspace\deeo-ai-poc
docker-compose ps
docker-compose up -d  # Si services down
```

**2. Erreur TypeScript sur imports** :
→ Vérifier que `tsconfig.json` contient :
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

**3. Menu mobile ne s'affiche pas** :
→ Vérifier que Tailwind classes `md:hidden` et `md:flex` fonctionnent  
→ Rebuild si nécessaire : `npm run build`

**4. Active states ne fonctionnent pas** :
→ Vérifier que `useLocation` de react-router-dom est importé  
→ Vérifier les conditions `isActive(path)`

---

## 🎯 RAPPEL OBJECTIF

**Vous créez l'architecture de base de DEEO.AI - la fondation sur laquelle tout le reste sera construit.**

Cette étape est critique : un layout solide, une navigation intuitive, et une structure claire garantissent le succès des étapes suivantes.

**Excellence. Quality. Impact.** 🚀

---

**Bon courage !** 💪

**Generated by**: Claude Sonnet 4.5  
**Date**: 18 Novembre 2025  
**Project**: DEEO.AI - Phase 4 Étape 2
