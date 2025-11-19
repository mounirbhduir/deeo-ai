/**
 * Progress Component
 * Simple progress bar for visualizing completion percentage
 */

import clsx from 'clsx'

interface ProgressProps {
  value: number // 0-100
  className?: string
  variant?: 'primary' | 'success' | 'warning' | 'error'
}

export function Progress({
  value,
  className,
  variant = 'primary',
}: ProgressProps) {
  const clampedValue = Math.min(100, Math.max(0, value))

  return (
    <div
      className={clsx(
        'w-full bg-gray-200 rounded-full overflow-hidden',
        className
      )}
    >
      <div
        className={clsx('h-full transition-all duration-300 rounded-full', {
          'bg-indigo-600': variant === 'primary',
          'bg-green-600': variant === 'success',
          'bg-yellow-600': variant === 'warning',
          'bg-red-600': variant === 'error',
        })}
        style={{ width: `${clampedValue}%` }}
      />
    </div>
  )
}
