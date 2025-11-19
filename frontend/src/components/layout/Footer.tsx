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
