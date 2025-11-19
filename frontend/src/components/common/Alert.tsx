import { ReactNode, HTMLAttributes } from 'react'
import clsx from 'clsx'
import { CheckCircle, AlertTriangle, XCircle, Info, X } from 'lucide-react'

interface AlertProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode
  variant: 'success' | 'warning' | 'error' | 'info'
  title?: string
  onClose?: () => void
}

const icons = {
  success: CheckCircle,
  warning: AlertTriangle,
  error: XCircle,
  info: Info,
}

const styles = {
  success: 'bg-green-50 border-green-200 text-green-800',
  warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
  error: 'bg-red-50 border-red-200 text-red-800',
  info: 'bg-blue-50 border-blue-200 text-blue-800',
}

const iconColors = {
  success: 'text-green-600',
  warning: 'text-yellow-600',
  error: 'text-red-600',
  info: 'text-blue-600',
}

export function Alert({
  children,
  variant,
  title,
  onClose,
  className,
  ...props
}: AlertProps) {
  const Icon = icons[variant]

  return (
    <div
      className={clsx(
        'flex items-start p-4 border rounded-lg',
        styles[variant],
        className
      )}
      role="alert"
      {...props}
    >
      <Icon className={clsx('h-5 w-5 flex-shrink-0 mr-3', iconColors[variant])} />

      <div className="flex-1">
        {title && (
          <h3 className="font-semibold mb-1">{title}</h3>
        )}
        <div className="text-sm">{children}</div>
      </div>

      {onClose && (
        <button
          onClick={onClose}
          className="flex-shrink-0 ml-3 hover:opacity-70 transition-opacity"
          aria-label="Close alert"
        >
          <X className="h-5 w-5" />
        </button>
      )}
    </div>
  )
}
