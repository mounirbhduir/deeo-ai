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
        La page que vous recherchez n&apos;existe pas ou a été déplacée.
      </p>
      <Link to="/">
        <Button>
          <Home className="mr-2 h-5 w-5" />
          Retour à l&apos;accueil
        </Button>
      </Link>
    </div>
  )
}
