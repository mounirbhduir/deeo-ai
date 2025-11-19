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
          La fonctionnalité de recherche avancée sera disponible à l&apos;Étape 5.
        </p>
      </div>
    </div>
  )
}
