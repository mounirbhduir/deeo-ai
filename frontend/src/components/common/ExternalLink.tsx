/**
 * ExternalLink Component
 *
 * Reusable component for displaying external links with consistent styling.
 * Used for DOI, arXiv, Semantic Scholar, and other external resources.
 */

import { ExternalLink as ExternalLinkIcon } from 'lucide-react'

interface ExternalLinkProps {
  href: string
  label: string
  value: string
  icon?: boolean
  className?: string
}

export const ExternalLink = ({
  href,
  label,
  value,
  icon = true,
  className = '',
}: ExternalLinkProps) => {
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <span className="text-gray-600 font-medium min-w-[120px]">{label}:</span>
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="text-blue-600 hover:text-blue-800 hover:underline flex items-center gap-1 transition-colors"
      >
        {value}
        {icon && <ExternalLinkIcon className="w-4 h-4" />}
      </a>
    </div>
  )
}
