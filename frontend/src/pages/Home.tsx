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
          Explorez l&apos;écosystème des publications scientifiques en Intelligence
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
